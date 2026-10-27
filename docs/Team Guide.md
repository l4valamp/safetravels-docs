# Team guide: write and sync

The website updates automatically after your changes reach GitHub. You never
need to build it yourself. These steps are for a desktop computer.

## Set up once

1. Install Obsidian, Git, and GitHub Desktop. Sign in to GitHub Desktop with your
   own account and accept the team's repository invitation. On Windows, install
   Git for Windows as well: the Obsidian plugin needs the `git` command. Set your
   own name/email in GitHub Desktop's Git settings.
2. In GitHub Desktop, choose **File > Clone repository**, select
   `l4valamp/safetravels-docs`, and clone it to a local folder. Keep the branch
   on `main` unless your maintainer gives you a different workflow. Use Clone,
   not Download ZIP: a ZIP cannot sync changes back.
3. In Obsidian, choose **Open folder as vault**, then select the **docs** folder
   inside the cloned `safetravels-docs` folder. Keep the whole cloned folder.
4. In **Settings > Community plugins**, enable community plugins, browse for
   **Git** (Obsidian Git), install it, and enable it.
5. In the Git plugin settings, enable **Pull on startup** and **Pull on
   commit-and-sync**. Leave **Custom base path** and **Custom Git directory path**
   empty: desktop Git discovers the repository one level above `docs`.
   Restart Obsidian if you installed Git while it was open.
6. Open the command palette (`Ctrl+P`, or `Cmd+P` on Mac), run **Git: Pull**, and
   check it succeeds. If authentication fails, ask the maintainer to help connect
   your locally installed Git to your GitHub account. Signing into Desktop alone
   may not authenticate a separate Git installation. Never paste a password or
   token into a note or a tracked settings file.

No other plugin, exporter, or Python setup is required. Automatic sync is
optional; start with the manual daily steps below so errors are easy to notice.

## Each time you work

1. Run **Git: Pull** before editing. Coordinate with anyone working on the same note.
2. Write normally. For a new documentation page, use the Page Template. Keep its
   `page` tag, and use Text in `Categories`, such as `[[Tech]]`, for category tables.
3. Run **Git: Commit-and-sync** when ready to share. Wait for it to finish before
   closing Obsidian. Your changes should appear on GitHub; the website usually
   follows within a few minutes. Older plugin versions may call this **Create
   backup**. Use the command that commits, pulls, and pushes.

## If something goes wrong

- **Sync fails:** your local writing is still there. Copy important unsynced text
  somewhere outside the repository first. Check your connection and the error;
  retry once. If it still fails, send the error to the maintainer. Do not choose
  Discard, reset, delete the vault, or force-push.
- **Two people edited the same note:** Git often combines different sections. If
  it reports a conflict, pause edits to that note and ask the other author or
  maintainer to help. The Git Source Control view lists conflicted files. Review
  both versions together, keep the intended combined text, mark the file resolved,
  then commit-and-sync. Do not blindly choose “ours” or “theirs”: either can remove
  someone's work. Remove any conflict markers such as `<<<<<<<` before finishing.
- **Sync succeeds but the site stays old:** check the latest **Deploy
  Documentation** run on the repository's Actions page. Send a failed run to the
  maintainer. Your notes are saved on GitHub even if website publication fails.

Plugin reference: [Obsidian Git documentation](https://publish.obsidian.md/git-doc).
