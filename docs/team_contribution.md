# Team Contribution & Project Defense Statement

## Note on Individual Submission
Hayden and I originally intended to work together as a team on this project, but we could not figure out an effective workflow to collaborate cleanly on the same codebase and repository. Because I also wanted to gain hands-on experience building and understanding the full stack myself, we ultimately decided that each of us would build and deploy our own complete system independently.

| Team member | Main responsibilities | Key calculation or design decision I can explain | Approximate commits |
|---|---|---|---|
| Jonathan Mey | Full-stack implementation: data loading and merge checks, Power BI reconciliation, sleek modern dark-mode dashboard with preloaded data and upload priority, analytical functions, Gemini function-calling integration, rules-based fallback, automated testing, and documentation | Why Survey Results is not joined to Sales (different grain: store-year vs. product-store-month), how `check_merge()` verifies that every join keeps 25,200 rows and $42,174,440, how byte-keyed caching updates all figures immediately on a +$1,000 upload, and how the number guard prevents the assistant from stating unverified figures | 20+ |

## Key defense topics

- How total revenue is calculated ($42,174,440 across 25,200 rows), and why it matches Power BI row for row.
- How the app preloads default data on startup and recalculates immediately after a modified upload (the cache is keyed on each file's byte contents, with uploaded files taking priority).
- What the central dispatcher (`run_tool`) does, and why the language model can only choose among the 10 named functions.
- How the number check (`unsupported_numbers`) stops Gemini from stating any figure the analytical tools did not calculate.
- Why the assistant refuses profit questions and adds explicit caveats and decision limits to "should we" and "does X cause Y" questions.
