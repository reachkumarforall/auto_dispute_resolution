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



