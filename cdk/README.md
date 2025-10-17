# AWS CDK deployment (optional)

This CDK app deploys the Dockerized FastAPI service to AWS ECS Fargate behind an Application Load Balancer in eu-central-1 (Frankfurt).

Requirements:
- An AWS account with credentials configured locally (AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY)
- Node.js/npm for the CDK CLI: `npm install -g aws-cdk`
- Python CDK libs installed in your venv: `pip install -r requirements.txt`

Bootstrap (once per account/region):

```powershell
cdk bootstrap
```

Build and push the image to ECR:

```powershell
# from repo root
docker build -t python-mastery-portfolio .
aws ecr get-login-password --region eu-central-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.eu-central-1.amazonaws.com
aws ecr create-repository --repository-name python-mastery-portfolio --region eu-central-1

docker tag python-mastery-portfolio:latest <account>.dkr.ecr.eu-central-1.amazonaws.com/python-mastery-portfolio:latest

docker push <account>.dkr.ecr.eu-central-1.amazonaws.com/python-mastery-portfolio:latest
```

Deploy the stack:

```powershell
# set env or rely on your default profile/region
$env:CDK_DEFAULT_REGION = "eu-central-1"
# optional: $env:CDK_DEFAULT_ACCOUNT = "123456789012"

cd cdk
python app.py
cdk deploy
```

The CDK output shows the LoadBalancer DNS. Open `http://<dns>/fib/10`.

Note: CDK code is not part of the test suite and is provided as an optional, deployable example.