# Skills to Extensions Converter

A command-line tool to convert Anthropic Claude skills into self-contained Google Gemini extensions.

## Overview

This project provides a Python script that automates the migration of Claude skills to the Gemini extension format. It recursively finds skills, converts them, and injects a universal MCP server that allows the extension to read its own files.

Once installed in the Gemini CLI's global directory, all skills are **loaded into the model's context on startup**, giving it immediate awareness of its full range of capabilities.

## Features

-   **Recursive Conversion:** Automatically finds all valid skills (`SKILL.md`) in a directory and its subdirectories.
-   **Global Context Awareness:** All installed skills are loaded on startup, allowing the model to know its full capabilities from the first prompt.
-   **Self-Contained Extensions:** Each converted skill becomes a standalone Gemini extension with a built-in file-reading server.
-   **Safe and Transparent:** Converts skills to a local output folder, giving you full control over the installation process.

## Prerequisites

-   [Python](https://www.python.org/downloads/) (version 3.7 or higher)
-   [Google Gemini CLI](https://github.com/google-gemini/gemini-cli) installed and configured.
-   [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) installed.
-   The `fastmcp` Python library. Install it once with pip:
    ```bash
    pip install fastmcp
    ```

## End-to-End Tutorial: Convert, Install, and Verify

This guide will walk you through cloning the official Anthropic skills repository, converting them, and installing them for global use.

### Step 1: Get the Source Skills

First, clone the official skill repository from Anthropic into a local folder.

```bash
git clone https://github.com/anthropics/skills.git
```

### Step 2: Install the Converter Script

Next, we will install the converter so it can be run as a local Gemini command.

```bash
# Clone this repository
git clone https://github.com/simongwatts/skills-to-extensions.git

# Create the gemini commands directory if it doesn't exist
mkdir -p ~/.gemini/commands

# Copy the two necessary files into the gemini commands directory
cp skills-to-extensions/skill_converter.py ~/.gemini/commands/
cp skills-to-extensions/server.py ~/.gemini/commands/
```

### Step 3: Run the Conversion

Navigate into the `skills` directory that you cloned in Step 1 and run the converter script.

```bash
# Change directory to the source skills
cd skills

# Run the conversion process. The output will be in a new 'converted_skills' folder.
python ~/.gemini/commands/skill_converter.py . --output ./converted_skills
```

### Step 4: Manually Install the Extensions

To make the extensions available globally, move them from the `converted_skills` folder to the Gemini CLI's dedicated extensions directory.

```bash
# Create the destination directory if it doesn't exist
mkdir -p ~/.gemini/extensions

# This command moves all converted extensions to the correct location.
mv ./converted_skills/* ~/.gemini/extensions/
```

### Step 5: Verify the Global Context

Now, we will confirm that the Gemini model is aware of all the new skills right from the start.

1.  **Launch the Gemini CLI** in interactive mode from any directory:
    ```bash
    gemini
    ```

2.  **Ask the model what skills it has.** Because all global extensions were loaded on startup, the model can summarize its capabilities from the combined context of all `SKILL.md` files.
    ```
    gemini> /extensions list
    gemini> /mcp list
    gemini> what skills do you have in context?
    ```
    *Expected output (the model will generate a summary similar to this):*
    ```
    ✦ I have the following skills available:

    * algorithmic-art: Creates algorithmic art using p5.js.
    * artifacts-builder: Builds complex HTML artifacts using React and Tailwind CSS.
    * brand-guidelines: Applies Anthropic's brand colors and typography.
    * canvas-design: Creates visual art in .png and .pdf documents.
    * docx: Creates, edits, and analyzes .docx files.
    * internal-comms: Helps write internal communications like status reports and newsletters.
    * mcp-builder: Creates MCP servers to interact with external services.
    * pdf: Manipulates PDF files (extract text, merge, split, etc.).
    * pptx: Creates, edits, and analyzes .pptx presentations.
    * skill-creator: Helps create new skills.
    * slack-gif-creator: Creates animated GIFs optimized for Slack.
    * template-skill: A template for creating new skills.
    * theme-factory: Styles artifacts with pre-set or custom themes.
    * webapp-testing: Tests local web applications using Playwright.
    * xlsx: Creates, edits, and analyzes spreadsheet files.    ```
This confirms the installation was successful and the model is ready.

### Step 6: Start Using Your Skills (Example Prompts)

Now that all skills are loaded into the model's context, you can make high-level requests without needing to specify the `@` tool name for every command. Here are some examples to try:

---

**Creative and Technical Skills:**

> **"Using the algorithmic-art skill, envision a dynamic tapestry woven from the echoes of forgotten signals. Particles,
  each a fragment of residual energy, drift through an invisible force field, their trajectories subtly influenced by
  the phantom currents of past interactions. As they move, they leave behind luminous trails that slowly fade, creating
  an ever-shifting landscape of ephemeral light and shadow. The art should capture the beauty of decay and the
  persistent memory of motion, where order emerges from the gentle chaos of countless individual paths. The subtle
  conceptual seed for this piece is 'temporal resonance' – the visual manifestation of lingering energetic imprints in a
  fluid, digital space."**
>
> *This will leverage the `algorithmic-art-ext` skill.*

---

**Meta Skills (Skills about creating skills):**

> **"I want to create a new skill for interacting with the GitHub API. What are the key files I need and what should I put in the SKILL.md?"**
>
> *This will use the `skill-creator-ext` to guide you through the process.*

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE.txt) file for details.