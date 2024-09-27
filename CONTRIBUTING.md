# Contributing to the Hacktoberfest Repository

Welcome to the Speak-To-Docs project repository put together by the Microsoft Learn Student Ambassadors towards Hacktoberfest 2024! We appreciate your interest in contributing to our projects. Please read this guide to understand how you can participate and make meaningful contributions.

## How to Install Dependencies and Work on the Project Locally

1. **Clone the Repository:**

   From your terminal, clone your forked repository and name it `speak-to-docs`.

   ```bash
   # Replace {user_name} with your GitHub username
   git clone https://github.com/{user_name}/speak-to-docs.git
   ```

2. **Set Up Virtual Environment:**

   Create a virtual environment named `speak-to-docs`.

   ```bash
   # Windows
   python -m venv speak-to-docs

   # macOS or Linux
   python3 -m venv speak-to-docs
   ```

   Activate the virtual environment:

   ```bash
   # Windows
   speak-to-docs\Scripts\activate

   # macOS or Linux
   source speak-to-docs/bin/activate
   ```

   Install necessary dependencies:

   ```bash
   cd speak-to-docs
   pip install -r requirements.txt
   ```

   Add the virtual environment to Jupyter Kernel (if contributing to Projects 1 and/or 3):

   ```bash
   python -m ipykernel install --user --name=speak-to-docs
   ```

3. **Work on Your Contributions:**

   - For **Project 1: SPEAK-TO-DOCS RAG PROJECT**, follow the guidelines in `Project_1` directory.

4. **Commit and Push:**

   After making changes, commit them and push to your forked repository.

   ```bash
   git add .
   git commit -m "{COMMIT_MESSAGE}"
   git push
   ```

5. **Create a Pull Request:**

   Create a pull request to merge your changes into the main repository.

## 🏢 Project 1: SPEAK-TO-DOCS RAG PROJECT

Contribute to RAG project tasks:

### Contribution Guidelines:

1. Clone the repository and follow the [local setup instructions](#how-to-install-dependencies-and-work-on-the-project-locally).

2. Create a folder under the `Project_1` directory following the naming convention:
   - Folder Name: `speak_to_docs_{GitHub_Username}`

   For example, if your GitHub username is `octocat`, your folder should be named `speak_to_docs_octocat`.

3. Work on project tasks in your notebook.

4. The team will evaluate the model's performance using a separate test dataset.

5. Make a pull request when ready.


## ✔️ General Guidelines

- Ensure your code is well-documented and follows best practices.

- Provide a descriptive pull request explaining the purpose of your changes.

- Be respectful and collaborative. Feel free to ask questions and seek assistance from other contributors or maintainers.

- Happy hacking! We appreciate your contributions to make this project better.

If you have any questions or need assistance, please feel free to reach out to us.

**Happy Hacking!**

## 🔗 Links to Resources

1. [How to Do Your First Pull Request](https://youtu.be/nkuYH40cjo4?si=Cb6U2EKVR_Ns4RLw)
2. [Azure Document Intelligence](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/overview?wt.mc_id=studentamb_271760)
3. [Process and Translate Speech with Azure AI Speech Services](https://learn.microsoft.com/en-gb/training/paths/process-translate-speech-azure-cognitive-speech-services/?wt.mc_id=studentamb_217190)
4. [How to Translate Text with Azure AI Translator in Python](https://learn.microsoft.com/en-us/azure/ai-services/translator/quickstart-text-rest-api?tabs=python#translate-text?wt.mc_id=studentamb_217190)
5. [Azure Speech Service documentation](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/?wt.mc_id=studentamb_217190)
6. [Customizing an LLM on Azure](https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/customizing-llms?wt.mc_id=studentamb_271760)
