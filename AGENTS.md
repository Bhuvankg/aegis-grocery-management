# Instructions for coding agents

Read `skills/aegis-ai/skill.md` before making changes. Treat the product invariants in that file as mandatory.

Work phase by phase. Inspect current implementation first, preserve existing behavior, use migrations for database changes, and add tests for every security boundary. Never implement admin-only security solely in the frontend. Never add public admin registration. Demo payment must remain simulated and must not collect card data. Keep secrets out of source control.
