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

These steps guide you through deploying the Streamlit client application on an OCI Compute Virtual Machine (VM). This guide assumes you are using **Oracle Linux 9**.

### Step 1: Prepare Your Code for Deployment

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
    *   **Image and Shape:** Select **Oracle Linux 9**. Choose an appropriate shape (an "Always Free" eligible shape is a good start).
    *   **Networking:** Ensure it's being created in a VCN with a **Public Subnet** and select `Assign a public IPv4 address`.
    *   **Add SSH Keys:** Select `Generate a key pair for me` and **save both the private and public keys**. You will need the private key to connect.

3.  **Create:** Click `Create`. Once the instance is `RUNNING`, note its **Public IP Address**.

### Step 3: Deploy the Application to the VM

1.  **Connect to the VM via SSH:**
    ```bash
    # Replace 'path/to/your/private-key' and 'your-vm-public-ip'
    ssh -i path/to/your/private-key opc@your-vm-public-ip
    ```

2.  **Install Git and Clone Your Repo:**
    ```bash
    sudo dnf install git -y
    git clone <your-private-repo-url.git>
    cd <your-repo-name> 
    ```

3.  **Install Python 3.11:** The OCI SDK requires Python 3.10+. We will install Python 3.11.
    ```bash
    # Install the Python 3.11 module stream
    sudo dnf module install python311 -y
    
    # Install the development tools for Python 3.11
    sudo dnf install python3.11-devel -y
    ```

4.  **Create a Virtual Environment:**
    ```bash
    # Create the virtual environment using python3.11
    python3.11 -m venv .venv
    
    # Activate the new environment
    source .venv/bin/activate
    ```

5.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### Step 4: Configure OCI Authentication on the VM

The application code expects to find an OCI configuration file and a corresponding API key on the VM. This method is used when Instance Principals are not configured.

**4.1. Generate a New OCI API Key (No Passphrase)**

First, generate a new API key on your local machine that is **not** protected by a passphrase.

1.  In the OCI Console, navigate to **Profile Icon** -> **Your Username** -> **API Keys**.
2.  Click **Add API Key** and select **Generate API Key Pair**.
3.  Click **Download Private Key** and save the `.pem` file to a secure location on your local machine (e.g., `C:\Users\your_user\.oci\`).
4.  **Crucially, leave the "Passphrase" field blank.**
5.  Click **Add**.
6.  Update your **local** `~/.oci/config` file with the new `fingerprint` and ensure the `key_file` path points to the new `.pem` file you just downloaded.

**4.2. Transfer Config and Key Files to the VM**

Run these commands from your **local terminal** (e.g., Git Bash) to copy the necessary files to the VM.

1.  **Create the `.oci` directory on the VM:**
    ```bash
    ssh -i <path_to_your_ssh_key> opc@<vm_public_ip> "mkdir -p /home/opc/.oci"
    ```

2.  **Copy your local `config` file to the VM:**
    ```bash
    scp -i <path_to_your_ssh_key> C:/Users/your_user/.oci/config opc@<vm_public_ip>:/home/opc/.oci/
    ```

3.  **Copy your new (no passphrase) `.pem` key file to the VM:**
    ```bash
    scp -i <path_to_your_ssh_key> C:/Users/your_user/.oci/oci_api_key.pem opc@<vm_public_ip>:/home/opc/.oci/
    ```

**4.3. Verify the `key_file` Path on the VM**

The `config` file you copied contains a Windows-style path for the `key_file`. You must edit it on the VM to use the correct Linux path.

1.  **Connect to the VM via SSH** and open the config file:
    ```bash
    ssh -i <path_to_your_ssh_key> opc@<vm_public_ip>
    nano /home/opc/.oci/config
    ```
2.  **Change the `key_file` line** from the Windows path to the correct Linux path:
    ```ini
    # Change this:
    key_file=C:\Users\your_user\.oci\oci_api_key.pem
    
    # To this:
    key_file=/home/opc/.oci/oci_api_key.pem
    ```
3.  Save the file and exit (`Ctrl+X`, then `Y`, then `Enter`).

### Step 5: Configure Networking and Run the App

We will run the app on port `8080` and forward traffic from the standard HTTP port `80` to it.

1.  **Configure OCI Security List:**
    *   In the OCI Console, navigate to your VM's Subnet -> Security List.
    *   Click `Add Ingress Rules`.
    *   **Source CIDR:** `0.0.0.0/0`
    *   **IP Protocol:** `TCP`
    *   **Destination Port Range:** `80` (for public access).
    *   Click `Add Ingress Rules`.

2.  **Configure the VM's Firewall (`firewalld`):**
    ```bash
    # Open port 80 for incoming public traffic
    sudo firewall-cmd --zone=public --add-port=80/tcp --permanent
    
    # Open port 8080 for the app to listen on internally
    sudo firewall-cmd --zone=public --add-port=8080/tcp --permanent
    
    # Enable masquerading to allow traffic routing
    sudo firewall-cmd --zone=public --add-masquerade --permanent
    
    # Add the rule to forward traffic from port 80 to 8080
    sudo firewall-cmd --zone=public --add-forward-port=port=80:proto=tcp:toport=8080 --permanent
    
    # Reload the firewall to apply all rules
    sudo firewall-cmd --reload
    ```

3.  **Run the Streamlit App on the VM:**
    *   Inside your SSH session (with the virtual environment still active), run the app on port 8080.
    ```bash
    streamlit run app_ui.py --server.port 8080 --server.address=0.0.0.0
    ```

4.  **Access the App:**
    *   Open a web browser and navigate to your VM's public IP address. **Do not add a port number.**
    `http://<your-vm-public-ip>`