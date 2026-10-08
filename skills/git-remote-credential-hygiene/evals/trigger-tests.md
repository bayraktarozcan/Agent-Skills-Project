# Trigger tests

Should fire (3):

1. "Check whether my git remotes hide passwords in their URLs."
2. "Move the token out of my .git/config into the OS credential
   manager and prove push still works."
3. "Audit fetch and push authentication on both GitHub and GitLab
   remotes without printing secrets."

Should NOT fire (2):

1. "Rewrite git history to purge a file committed last year."
2. "Set up Vault as our team secrets backend with dynamic credentials."
