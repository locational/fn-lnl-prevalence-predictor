## Running locally

`echo "{\"polys\":$(cat ZAF_adm2.json | jq '. | tostring'), \"stats\": \"sum\"}" | python3 index.py` or similar is very helpful.