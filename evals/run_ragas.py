# evals/run_evals.py
import asyncio
import json
import httpx

API_URL = "http://localhost:8000"

async def evaluate():
    with open("evals/golden_dataset.json") as f:
        golden = json.load(f)

    results = []

    async with httpx.AsyncClient() as client:
        for item in golden:
            q = item["question"]
            expected = item["ground_truth"].lower()

            # Get answer
            answer = ""
            async with client.stream(
                "POST", f"{API_URL}/query",
                json={"question": q, "top_k": 5},
                timeout=60,
            ) as resp:
                async for line in resp.aiter_lines():
                    if line.startswith("data: "):
                        answer += line[6:]

            # Get contexts
            r = await client.post(
                f"{API_URL}/retrieve",
                json={"question": q, "top_k": 5},
                timeout=30,
            )
            chunks = [c["content"].lower() for c in r.json()["chunks"]]

            # Simple checks
            answer_lower = answer.lower()
            context_hit = any(
                word in " ".join(chunks)
                for word in expected.split()
                if len(word) > 4
            )
            answer_hit = any(
                word in answer_lower
                for word in expected.split()
                if len(word) > 4
            )

            results.append({
                "question": q,
                "expected": item["ground_truth"],
                "answer": answer.strip(),
                "context_hit": context_hit,
                "answer_hit": answer_hit,
            })

            status = "✅" if answer_hit else "❌"
            print(f"{status} Q: {q}")
            print(f"   Expected : {item['ground_truth']}")
            print(f"   Got      : {answer.strip()[:100]}")
            print()

    # Summary
    total = len(results)
    passed = sum(1 for r in results if r["answer_hit"])
    ctx_passed = sum(1 for r in results if r["context_hit"])

    print(f"=== RESULTS ===")
    print(f"Answer accuracy : {passed}/{total} ({100*passed//total}%)")
    print(f"Context recall  : {ctx_passed}/{total} ({100*ctx_passed//total}%)")

    with open("evals/results.json", "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print("Saved to evals/results.json")

if __name__ == "__main__":
    asyncio.run(evaluate())