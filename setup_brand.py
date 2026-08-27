import os
import json
import logging
from typing import Dict, Any

# Configure professional enterprise logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

class BrandConfigurator:
    """
    Enterprise configuration manager for the Daily LinkedIn Posts Pipeline.
    Handles loading brand configurations and interpolating templates across the codebase.
    """

    def __init__(self, config_path: str = "brand_config.json") -> None:
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        self.replacements: Dict[str, str] = {}
        self.extensions_to_process = ('.py', '.cjs', '.js', '.md', '.sh', '.html')

    def load_config(self) -> bool:
        """Loads the JSON configuration file from disk."""
        if not os.path.exists(self.config_path):
            logger.error(f"Configuration file '{self.config_path}' not found. Please create it based on the README instructions.")
            return False

        try:
            with open(self.config_path, "r", encoding="utf-8") as file:
                self.config = json.load(file)
            logger.info("Successfully loaded brand configuration.")
            self._build_replacement_map()
            return True
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON in '{self.config_path}': {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error loading configuration: {e}")
            return False

    def _build_replacement_map(self) -> None:
        """Builds the dictionary mapping template tags to actual configuration values."""
        self.replacements = {
            "{{BRAND_NAME}}": self.config.get("BRAND_NAME", "Company Name"),
            "{{BRAND_SHORT_NAME}}": self.config.get("BRAND_SHORT_NAME", "Company"),
            "{{BRAND_SHORT_NAME_LOWER}}": self.config.get("BRAND_SHORT_NAME", "company").lower(),
            "{{AUTHOR_NAME}}": self.config.get("AUTHOR_NAME", "Author Name"),
            "{{AUTHOR_NAME_LOWER}}": self.config.get("AUTHOR_NAME", "author").lower(),
            "{{AUTHOR_TYPE}}": self.config.get("AUTHOR_TYPE", "{{AUTHOR_TYPE}}"),
            "{{BRAND_DOMAIN}}": self.config.get("BRAND_DOMAIN", "Industry"),
            "{{TARGET_AUDIENCE}}": self.config.get("TARGET_AUDIENCE", "Target audience"),
            "{{BRAND_SOCIAL_HANDLE}}": self.config.get("BRAND_SHORT_NAME", "company").lower(),
            "schedule_company.cjs": self.config.get("POST_SCHEDULE_COMPANY", "schedule_company.cjs"),
            "schedule_personal.cjs": self.config.get("POST_SCHEDULE_PERSONAL", "schedule_personal.cjs")
        }

    def process_file(self, filepath: str) -> bool:
        """
        Reads a file, applies the template replacements, and overwrites if changes occurred.
        Returns True if the file was updated, False otherwise.
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception:
            # Skip unreadable or binary files
            return False

        original_content = content
        for tag, value in self.replacements.items():
            content = content.replace(tag, value)
            
        if content != original_content:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True
            except Exception as e:
                logger.warning(f"Failed to write updates to '{filepath}': {e}")
                return False
        return False

    def execute(self) -> None:
        """Executes the pipeline personalization process across the entire repository."""
        logger.info("Starting pipeline brand personalization process...")
        if not self.load_config():
            return

        updated_files_count = 0

        for root, dirs, files in os.walk('.'):
            # Ignore hidden directories, node_modules, and output folders
            if any(exclude in root for exclude in ['node_modules', '.git', 'sample-outputs', 'scratch']):
                continue
                
            for file in files:
                if file.endswith(self.extensions_to_process) and file != os.path.basename(__file__):
                    filepath = os.path.join(root, file)
                    if self.process_file(filepath):
                        updated_files_count += 1

        logger.info(f"Successfully configured {updated_files_count} files with your brand details!")
        logger.info("You can now run the pipeline scripts directly.")

if __name__ == "__main__":
    configurator = BrandConfigurator()
    configurator.execute()
