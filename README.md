# reddit-cyborg

Reddit Cyborg is a personal automation assistant running under my main account /u/captainmeta4. It is similar to AutoModerator in design.

Reddit Cyborg is my only bot that is not available for easy widespread usage. This decision is due to its ability to issue automated subreddit bans based on arbitrarily specified criteria. While I have a specific and necessary use for this feature, please remember that automated bans are usually poor form.

If you are interested in running a clone of Cyborg yourself, feel free to fork the project.

# Valid Arguments

Cyborg operates on custom-specified rules in a manner similar to AutoModerator. The following is a list of available keys.

Matching criteria:

* `type` - must be `"both"`, `"link submission"`, `"text submission"`, or `"comment"`. Defaults to `"both"`
* `subreddit` - must be a `[list, of, subreddits]`
* `author_name` - must be a `[list, of, usernames]`
* `body` - must be a `[list, of, words]`. Applies only to comments and text submissions
* `domain` - must be a `[list.of, domai.ns]`. Applies only to link submissions
* `body_regex` - must be a `['list of one( or more)? regular expressions?']`. Applies only to comments and text submissions.
* `title` - must be a `[list, of, words]`. Applies only to submissions.

Outputs:

* `action` - **must be a list** containing at least one of `remove`, `remove_parent`, `spam`, `spam_parent`, `ban`, `ban_parent`, `report`, `report_parent`, `approve`, or `approve_parent`.
* `comment` - Comment to reply with. Comments are distinguished.
* `ban_duration` - Length of ban. Defaults to `None`. Use when `ban` or `ban_parent` are included in `action`.
* `ban_message` - Message given in ban notice. Defaults to empty string. Use when `ban` or `ban_parent` are included in `action`.
* `reason` - Action reason seen in mod log, ban notes, or report reason.
* `message` - Send a PM to the user.
* `message_subject` - Subject of message sent to user. Use with `message`.

Modifications:

* `invert` - Must be a list containing any subset of text-based input field names.
