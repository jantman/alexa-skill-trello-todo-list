data "archive_file" "pkg" {
  type        = "zip"
  source_dir  = "${path.module}/lambda_package/"
  output_path = "lambda_package.zip"
}

resource "aws_lambda_function" "lambda" {
  filename         = "${path.module}/lambda_package.zip"
  function_name    = "alexa-skill-trello"
  role             = "arn:aws:iam::860309399526:role/iam_for_lambda_monitoring"
  handler          = "skill.handler"
  source_code_hash = "${data.archive_file.pkg.output_base64sha256}"
  runtime          = "python3.6"

  environment {
    variables = {
      foo = "bar"
    }
  }
}

output "lambda_arn" {
  value = "${aws_lambda_function.lambda.arn}"
}

resource "aws_lambda_permission" "with_alexa" {
  statement_id  = "AllowExecutionFromAlexa"
  action        = "lambda:InvokeFunction"
  function_name = "${aws_lambda_function.lambda.function_name}"
  principal     = "alexa-appkit.amazon.com"
}
