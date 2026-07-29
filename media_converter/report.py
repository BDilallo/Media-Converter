class Report:
    def __init__(self):
        self.converted = 0
        self.copied = 0
        self.skipped = 0
        self.failed = 0
        self.copied_files = []
        self.skipped_files = []
        self.failed_files = []

    def record_converted(self):
        self.converted += 1

    def record_copied(self, name: str):
        self.copied += 1
        self.copied_files.append(name)

    def record_skipped(self, name: str):
        self.skipped += 1
        self.skipped_files.append(name)

    def record_failed(self, name: str):
        self.failed += 1
        self.failed_files.append(name)

    def print(self):
        print("\n==== SUMMARY ====")
        print(f"Converted: {self.converted}")
        print(f"Copied (already correct format): {self.copied}")
        if self.copied:
            print("  - Files already correct format:")
            for f in self.copied_files:
                print(f"    • {f}")

        print(f"Skipped: {self.skipped}")
        if self.skipped:
            print("  - Skipped files:")
            for f in self.skipped_files:
                print(f"    • {f}")

        print(f"Failed: {self.failed}")
        if self.failed:
            print("  - Failed files:")
            for f in self.failed_files:
                print(f"    • {f}")

        print("=================")
