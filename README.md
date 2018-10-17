# alexa-skill-trello-todo-list

Alexa skill to read your Trello todo list and add items to it

## Setting up the Skill

1. Create the Skill at https://developer.amazon.com/alexa/console/ask/ ; call the skill "trello" and paste the content of ``skill.json`` into the JSON Editor.
2. Run terraform to create the Lambda function (see below). Make sure to do this in one of the four Alexa supported regions (i.e. us-east-1).
3. _Optional:_ Open the AWS Console and browse to the Lambda function. Configure a test event called "LaunchRequest" using the "Amazon Alexa Start Session" template, save it, and test the function. Ensure it executes successfully.
4. Go back to the [Developer Portal](https://developer.amazon.com/edw/home.html#/skills/list) from step 1 and select the skill you created.
5. In the Endpoint tab, select "AWS Lambda ARN". Paste the ``lambda_arn`` terraform output in the "Default Region" box.
6. Click the "Save Endpoints" button near the top left of the panel. Make sure a popup confirms saving successfully.
7. Click the "test" tab along the top of the screen and test the skill in your browser.

## Terraform

Export some environment variables and then run terraform:

```bash
export TF_VAR_aws_region=us-east-1
export TF_VAR_aws_account_id=YOURaccountID
export TF_VAR_role_arn=YourLambdaRoleARN
export TF_VAR_skill_id=YourSkillID
terraform plan
```

## Development

If you need to update the Python dependencies, use ``./pip_install.sh`` to install dependencies.

## Troubleshooting

Set a ``DEBUG`` environment variable on the Lambda to enable debug-level logging.
