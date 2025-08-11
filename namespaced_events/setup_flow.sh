python parent_flow.py --branch bar --production argo-workflows create
python child_flow.py --config-value project '{"branch": "bar", "production":true}' argo-workflows create

python parent_flow.py --branch bar --production argo-workflows trigger


python parent_flow.py --branch baaz argo-workflows create
python child_flow.py --config-value project '{"branch": "baaz"}' argo-workflows create
python parent_flow.py --branch baaz argo-workflows trigger


python parent_flow.py argo-workflows create
python child_flow.py argo-workflows create
python parent_flow.py argo-workflows trigger
