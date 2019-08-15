COUNTER_TABLE_NAME=stellitime-api-counter
COUNTER_STACK_NAME=$(COUNTER_TABLE_NAME)-stack
AWS_DEFAULT_REGION=us-east-1

all: pre-install deploy_dynamodb_table test

test:
	@echo run tests here...

pre-install:
	pip3 install -r requirements.txt

deploy_dynamodb_table:
	aws cloudformation deploy \
     --template-file cloudformation/counter-table.yaml \
     --stack-name ${COUNTER_STACK_NAME} \
     --region $(AWS_DEFAULT_REGION)