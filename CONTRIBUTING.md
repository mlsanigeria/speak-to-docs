# Contributing to the Hacktoberfest Repository

Welcome to the **Speak-To-Docs** project repository, organized by the Microsoft Learn Student Ambassadors for Hacktoberfest 2024! This repository is dedicated to building and enhancing a **Speech-Enabled Retrieval-Augmented Generation (RAG) Solution**, dubbed "Speak-To-Docs." We're excited to have you contribute and improve this innovative project.

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

   Add the virtual environment to Jupyter Kernel if necessary:

   ```bash
   python -m ipykernel install --user --name=speak-to-docs
   ```

3. **Work on the Project:**

   - This repository is specifically for the **Speak-To-Docs** RAG project. Explore the project structure and check the **Issues** tab for tasks or bugs that you can address. 
   - You are encouraged to review the current implementation and contribute new features or improvements to the **Speech-Enabled RAG Solution**.

4. **Commit and Push Your Changes:**

   Once your contributions are ready, commit your changes and push them to your forked repository.

   ```bash
   git add .
   git commit -m "{COMMIT_MESSAGE}"
   git push
   ```

5. **Submit a Pull Request:**

   After pushing your changes, submit a pull request to merge them into the main repository. Make sure to include a clear and concise description of what your contribution entails.

## Project Structure:
The **Speech-Enabled RAG Solution** is a voice-powered interface that allows users to engage with their documents through speech. Look at it as a model that explains a document you want to read.

The project is structured as follows:
- **speech_to_docs**: This is the main directory for the project.
- **speech_to_docs/src**: This directory contains all the files that will house all the functionalities of the project: Speech transcription and synthesis, RAG model Solution and document reading.
- **speech_to_docs/src/rag_functions.py**: This file contains the function that checks for uploaded file compatibility, making sure it doesn't exceed 50 pages limit as well as the RAG model solution functionalities.
- **speech_to_docs/src/speech_io.py**: This files handles the speech_to_text/ text_to_speech function of the model by using **Azure Cognitive Services: Speech Transcription** (Speech-to-Text) and **Speech Synthesis** (Text-to-Speech).
- **speech_to_docs/requirements.txt**: This file lists the dependencies required to run the project.
- **speech_to_docs/README.md**: This file contains information about the project, including this guide
- **speech_to_docs/LICENSE**: This file contains the license information for the project.
- **speech_to_docs/CONTRIBUTING.md**: This file contains information about contributing to the project
- **speech_to_docs/CODE_OF_CONDUCT.md**: This file contains information about the purpose, policy and behaviour expected of the project.
- **speech_to_docs/LEADERBOARD.md**: This file contains information about the leaderboard (ranking of people with the highest PRs).


## How You Can Contribute:

1. Review the existing project code and issues to understand the functionality.
2. Find an open issue that matches your skills or propose a new feature.
3. Work on your contribution, test it thoroughly, and make sure it aligns with the project goals.
4. Submit your pull request with a clear explanation of your contribution.

## ✔️ General Contribution Guidelines

- Follow best practices for coding, including writing clean and well-documented code.
- Provide meaningful commit messages and detailed pull request descriptions.
- Respectfully collaborate and communicate with other contributors.
- Feel free to ask questions or seek guidance from project maintainers if needed.

**Happy hacking! We can't wait to see your amazing contributions!**

---

## 🔗 Links to Resources

1. [How to Do Your First Pull Request](https://youtu.be/nkuYH40cjo4?si=Cb6U2EKVR_Ns4RLw)
2. [Azure Document Intelligence](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/overview?wt.mc_id=studentamb_271760)
3. [Azure Document Intelligence-Code Implementation](https://learn.microsoft.com/azure/ai-services/document-intelligence/quickstarts/get-started-sdks-rest-api?view=doc-intel-3.0.0&pivots=programming-language-java?wt.mc_id=studentamb_405806)
4. [Use the fast transcription API (preview) with Azure AI Speech](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/fast-transcription-create?wt.mc_id=studentamb_217190)
5. [Quickstart: Convert text to speech](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/get-started-text-to-speech?pivots=programming-language-python?wt.mc_id=studentamb_217190)
6. [Fundamentals of Azure OpenAI Service](https://learn.microsoft.com/en-us/training/modules/explore-azure-openai/?wt.mc_id=studentamb_217190)
7. [Azure OpenAI Models: Deployment](https://learn.microsoft.com/azure/ai-services/openai/how-to/working-with-models?tabs=powershell?wt.mc_id=studentamb_405806)
8. [Azure Speech Service documentation](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/?wt.mc_id=studentamb_217190)
9. [Develop Generative AI solutions with Azure OpenAI Service](https://learn.microsoft.com/en-us/training/paths/develop-ai-solutions-azure-openai/?wt.mc_id=studentamb_217190)
10. [Langchain's DocArrayInMemoryStore Documentation](https://python.langchain.com/docs/integrations/vectorstores/docarray_in_memory/)
