variable "role_arn" {
  description = "Lambda execution role ARN"
}

variable "skill_id" {
  description = "The ID of the skill allowed to trigger this function"
}

variable "trello_app_key" {
  description = "Trello API app key"
}

variable "trello_token" {
  description = "Trello API token"
}

variable "trello_board_id" {
  description = "Trello board ID to operate on"
}

variable "trello_add_list_id" {
  description = "Trello List ID to add new cards to"
}

variable "trello_read_list_ids" {
  description = "Trello List IDs to read, as CSV"
}

variable "tags" {
  description = "Tags for Lambda function"
  type        = "map"
  default     = {}
}
