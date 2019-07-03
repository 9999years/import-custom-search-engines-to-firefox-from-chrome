# Import custom search engines to Firefox from Chrome

1. Create a folder for your search engines in your Firefox bookmarks called `Search Engines`
2. Backup Firefox bookmarks to JSON.
3. Determine where your Chrome database is:

    Operating System | Path
    ---------------- | ----
    Windows          | `"%USERPROFILE%\AppData\Local\Google\Chrome\User Data\Default\Web Data"`
    WSL              | `"/mnt/c/Users/USERNAME/AppData/Local/Google/Chrome/User Data/Default/Web Data"`
    macOS            | `"~/Library/Application Support/Google/Chrome/Default/Web Data"`

4. Run `bookmarks.py` to patch the exported bookmarks:

        bookmarks.py --title "Search Engines" \
                     --database DB_FNAME \
                     PATH_TO_BOOKMARKS_EXPORT.json \
                     PATH_TO_PATCHED_BOOKMARKS.json

   Where `DB_FNAME` is the database file located above,
   `PATH_TO_BOOKMARKS_EXPORT.json` is the backup of your bookmarks, and
   `PATH_TO_PATCHED_BOOKMARKS.json` is where you want to save the new
   bookmarks.

5. Restore your bookmarks from the newly-created JSON file.
