# Epistem Land Use Land Cover Classification Algorithm

This repository contains the core backend algorithms and modules for the Epistem land use land cover mapping platform.

## File Structure

- **`src/epistemx/`**: The core Python package for this project. It contains all the backend logic, helper functions, and modules for interacting with Google Earth Engine.
- **`notebooks/`**: Jupyter notebooks used for development, experimentation, and demonstrating the functionality of the core modules.
- **`home.py` & `pages/`**: A minimal Streamlit application for testing and demonstrating the backend algorithms.
- **`environment.yml`**: The environment file for creating a reproducible environment. It lists all necessary Python packages and dependencies.
- **`pyproject.toml`**: The standard Python project configuration file. It defines project metadata and core dependencies for `pip`.

## Getting Started

Follow these instructions to set up and run the project on your local machine.

### 1. Prerequisites

Before you begin, ensure you have the following installed on your system:

- **Git**: A version control system for cloning the repository. [Installation Guide](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git).
- **Python environment manager**: If you do not yet have one installed, we recommend [Miniforge](https://github.com/conda-forge/miniforge); it is lightweight, no-frills compared to Anaconda, and works well for this project. If you already have another Conda-compatible manager, you can continue using it.

To confirm these tools are available in your shell, run:

```powershell
git --version
conda --version
```

### 2. Set Up the Python Environment

Choose one of the following setup methods based on your needs:

#### Option A: Prepackaged Conda-Pack Environment (Windows 11 x64)

_Best for Windows 11 x64 machines - fastest setup with all dependencies pre-installed._

1. Download the prepackaged `epistemx` conda-pack archive from [SharePoint](https://icrafcifor.sharepoint.com/:u:/r/sites/EPISTEM/Shared%20Documents/EPISTEM%20Consortium/1%20Monitoring%20Technology/Prototyping/python_environment/epistemx.tar.gz?csf=1&web=1&e=eGbscP). You will need access to the EPISTEM SharePoint workspace.

2. Unpack the archive and make it usable on your machine by following [these instructions](https://gist.github.com/pmbaumgartner/2626ce24adb7f4030c0075d2b35dda32) for restoring a conda-pack environment. In short, place the archive in the directory where you keep your Conda environments and extract it. Example commands (adapt paths to your platform):

   ```powershell
   mkdir -p ~/epistemx
   tar -xzf epistemx.tar.gz -C ~/epistemx
   ```

3. Then, activate the environment and unpack it:

   ```powershell
   cd \path\to\epistemx
   .\Scripts\activate.bat
   .\Scripts\conda-unpack.exe
   ```

   The epistemx environment now includes all dependencies for Earth Engine, JupyterLab, and Streamlit.

4. Clone the repository and proceed to [Usage](#4-usage).

#### Option B: Build from `environment.yml` (macOS/Linux)

_Recommended for macOS and Linux systems, or if you prefer building the environment yourself._

1. Clone the repository first:

   ```bash
   git clone https://github.com/epistem-io/EpistemXBackend.git
   cd EpistemXBackend
   ```

2. Create the environment using the provided `environment.yml`:

   ```bash
   conda env create -f environment.yml -n epistemx
   conda activate epistemx
   ```

3. Proceed to [Usage](#4-usage).

#### Option C: GitHub Codespaces (Cloud-based, No Local Setup)

_Best for quick experimentation without local installation, or when working on different machines. Note: This option supports running the epistemx package and notebooks only; Streamlit applications are not supported in Codespaces._

1. **Create a Codespace** from the repository:
   - Navigate to the [EpistemXBackend repository](https://github.com/epistem-io/EpistemXBackend) on GitHub
   - Click the green **Code** button
   - Select **Codespaces** tab → **Create codespace on update_main**
   - Wait for the environment to initialize (typically 2-3 minutes)

2. **Start working with notebooks**:
   - Open the `notebooks/Module_implementation.ipynb` file in VS Code's notebook editor within the Codespace
   - When prompted, select the Python kernel provided by the Codespace environment
   - The required environment and package setup are already configured in Codespaces
   - Work through the notebook for step-by-step examples and module testing


**Codespaces Tips:**

- Notebooks run directly in VS Code's built-in notebook editor
- Long-running Earth Engine operations may take several minutes; monitor progress in cell outputs
- Download results locally by right-clicking files in the file explorer → **Download**
- Use the VS Code terminal (Ctrl+\`) for additional commands if needed
- Codespaces automatically save your work; you can return to the same Codespace later

### 3. Clone the Repository (Options A & B only)

**Note:** Skip this step if you're using GitHub Codespaces (Option C), as the repository is already cloned.

With the environment ready, clone the project and move into the repository:

```bash
git clone https://github.com/epistem-io/EpistemXBackend.git
cd \path\to\EpistemXBackend
```

### 4. Usage

Activate the `epistemx` environment (prepackaged or locally built) and use the tooling included in it.

#### Running the Jupyter Notebooks

Before launching, install the `epistemx` package into the active environment so notebooks can import the source modules:

```bash
python -m pip install -e .
```

Launch Jupyter Lab from the project root to explore the project's modules and workflows:

```bash
jupyter lab
```

#### Running the Jupyter Notebooks

Before launching, install the `epistemx` package into the active environment so notebooks can import the source modules:

```bash
python -m pip install -e .
```

Launch Jupyter Lab from the project root to explore the project's modules and workflows:

```bash
jupyter lab
```

Start with `Module_implementation.ipynb` in the `notebooks/` directory for a focused guide on individual module testing and development. This notebook provides step-by-step examples for working with the core epistemx modules.

#### Running the Streamlit Application

The included Streamlit app is a minimal implementation for testing the backend. To launch it, run the following command from the project's root directory:

```bash
python -m streamlit run home.py
```

This will open the application in your default web browser.
