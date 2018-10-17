provider "aws" {
  region              = "${var.aws_region}"
  allowed_account_ids = ["${var.aws_account_id}"]
}

data "archive_file" "pkg" {
  type        = "zip"
  source_dir  = "${path.module}/lambda_package/"
  output_path = "lambda_package.zip"
}

resource "aws_lambda_function" "lambda" {
  filename         = "${path.module}/lambda_package.zip"
  function_name    = "alexa-skill-trello"
  role             = "${var.role_arn}"
  handler          = "skill.handler"
  source_code_hash = "${data.archive_file.pkg.output_base64sha256}"
  runtime          = "python2.7"

  environment {
    variables = {
      TRELLO_APP_KEY       = "${var.trello_app_key}"
      TRELLO_TOKEN         = "${var.trello_token}"
      TRELLO_BOARD_ID      = "${var.trello_board_id}"
      TRELLO_ADD_LIST_ID   = "${var.trello_add_list_id}"
      TRELLO_READ_LIST_IDS = "${var.trello_read_list_ids}"
    }
  }
}

resource "aws_lambda_permission" "with_alexa" {
  statement_id       = "AllowExecutionFromAlexa"
  action             = "lambda:InvokeFunction"
  function_name      = "${aws_lambda_function.lambda.function_name}"
  principal          = "alexa-appkit.amazon.com"
  event_source_token = "${var.skill_id}"
}
