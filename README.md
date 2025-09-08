# Automated Dispute Resolution System

This project provides a Streamlit-based user interface for an automated dispute resolution system that uses a multi-agent workflow to analyze customer disputes.

## Setup Instructions

Follow these steps to set up and run the project on your local machine.

### 1. Create and Activate Virtual Environment

It is recommended to use a virtual environment to manage project dependencies.

*   **Create the environment:**
    ```bash
    python -m venv .venv
    ```

*   **Activate the environment:**
    *   On Windows:
        ```bash
        .venv\Scripts\activate
        ```
    *   On macOS/Linux:
        ```bash
        source .venv/bin/activate
        ```

### 2. Install Dependencies

Install all the required Python packages using the `requirements.txt` file.

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

The application requires API keys and other configuration details to be stored in an environment file.

1.  Create a directory named `config` in the root of the project if it doesn't already exist.
2.  Inside the `config` directory, create a new file named `.env`.
3.  Add your configuration details to the `.env` file. For example:
    ```
    # Example .env content
    OPENAI_API_KEY="your_openai_api_key_here"
    DATABASE_URL="your_database_connection_string_here"
    ```

## How to Run

### Run the Streamlit Web UI

To start the interactive web application, run the following command in your terminal:

```bash
streamlit run app_ui.py
```

### Run the Workflow Script

To execute the dispute resolution workflow directly from the command line and print the results to the console, use this command:

```bash
python -m src.workflows.dispute_resolution_workflow
```

## Deployment on OCI Compute VM

These steps guide you through deploying the Streamlit client application on an OCI Compute Virtual Machine (VM).

### Step 1: Prepare Your Code for Deployment

Your code needs to be accessible from the VM, preferably via a Git repository.

1.  **Initialize a Git Repository:** If you haven't already, initialize Git in your project folder.

2.  **Create a `.gitignore` file:** This is critical to prevent committing secrets and virtual environments. Create a file named `.gitignore` in your project root with the following content:
    ```
    # Environment files
    .env
    
    # Python virtual environment
    .venv/
    
    # Python caches
    __pycache__/
    *.pyc
    ```

3.  **Push to a Private Repository:** Create a new **private** repository on a service like GitHub and push your code to it.

### Step 2: Create and Configure the OCI Compute VM

1.  **Navigate to Compute Instances:** In the OCI Console, go to `Compute` -> `Instances`.

2.  **Create Instance:**
    *   **Name:** Give it a descriptive name (e.g., `dispute-resolution-app-vm`).
    *   **Image and Shape:** Choose an appropriate image (e.g., Oracle Linux or Ubuntu) and a shape (an "Always Free" eligible shape is a good start).
    *   **Networking:** Ensure it's being created in a VCN with a **Public Subnet** and select `Assign a public IPv4 address`.
    *   **Add SSH Keys:** Select `Generate a key pair for me` and **save both the private and public keys**. You will need the private key to connect.

3.  **Create:** Click `Create`. Once the instance is `RUNNING`, note its **Public IP Address**.

### Step 3: Deploy the Application to the VM

1.  **Connect to the VM via SSH:**
    *   Use the `ssh` command with your private key and the VM's public IP. The default username for Oracle Linux is `opc`.
    ```bash
    # Replace 'path/to/your/private-key' and 'your-vm-public-ip'
    ssh -i path/to/your/private-key opc@your-vm-public-ip
    ```

2.  **Install Git and Clone Your Repo:**
    *   Once connected, install Git:
    ```bash
    # For Oracle Linux / RHEL
    sudo dnf install git -y
    ```
    *   Clone your private repository:
    ```bash
    git clone <your-private-repo-url.git>
    cd <your-repo-name> 
    ```

3.  **Install Python and Create a Virtual Environment:**
    *   Install the Python development tools, which include `venv`:
    ```bash
    # For Oracle Linux / RHEL
    sudo dnf install python3-devel -y
    ```
    *   Create and activate the virtual environment:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

4.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Configure OCI Credentials:** The most secure method is using an **Instance Principal**. Your code should be configured to use this automatically when no API key config is found. No credential file is needed on the VM.

### Step 4: Run and Access Your Application

1.  **Open the Firewall Port:** You must open the Streamlit port (default 8501) in the OCI network security list.
    *   In the OCI Console, navigate to your VM's Subnet -> Security List.
    *   Click `Add Ingress Rules`.
    *   **Source CIDR:** `0.0.0.0/0` (Allows access from any IP).
    *   **IP Protocol:** `TCP`.
    *   **Destination Port Range:** `8501`.
    *   Click `Add Ingress Rules`.

2.  **Run the Streamlit App on the VM:**
    *   Back in your SSH session, inside the project directory with the virtual environment active, run the app:
    ```bash
    streamlit run app_ui.py
    ```

3.  **Access the App:**
    *   Open a web browser on your local machine and navigate to: `http://<your-vm-public-ip>:8501`