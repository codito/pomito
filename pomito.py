#!/usr/bin/env python
# Pomito - Pomodoro timer on steroids
# Main executable

if __name__ == "__main__":
    import os
    import sys
    from pomito import main

    if os.getenv("enable_esky") is not None:
        import traceback
        import esky
        from esky.finder import LocalVersionFinder

        # Experimental esky bootstrap
        if getattr(sys, "frozen", False):
            version_finder = LocalVersionFinder("/tmp/pomito_repo")
            app = esky.Esky(sys.executable, version_finder)

        try:
            app.auto_update()
        except Exception as e:
            print("ERROR UPDATING APP:", e)
            print(traceback.format_exc())

    sys.exit(main.main())
