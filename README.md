# Flask App README

This README provides instructions for running the Flask app locally using Gunicorn.

## Prerequisites

- Python (3.x recommended)
- Pip (Python package installer)

## Installation

1. Clone or download the search-app source code from the thesis submission supporting materials.
2. Install dependencies:
pip install -r requirements.txt

## Running the App Locally

1. Navigate to the app directory:
cd path/to/search-app-directory

2. Run the app using Gunicorn:
gunicorn app:app

3. Open your web browser and go to the local host to access the app.

## Troubleshooting

- If you encounter any issues, ensure that you have followed the installation steps correctly and that your environment is properly configured.

## Notes

- This app is not set up to run executable files due to Heroku's limitations. Refer to [Heroku documentation](https://devcenter.heroku.com/articles/dynos#ephemeral-filesystem) for more information.

## Cite this work

Our work is published in IEEE Transactions on Education. Cite using the following bibtex entry.

@article{QModuleBot,
  author    = {Mia Allen and Usman Naeem and Sukhpal Singh Gill},
  title     = {Q-Module-Bot: A Generative AI-Based Question and Answer Bot for Module Teaching Support},
  journal   = {IEEE Transactions on Education},
  year      = {2024},
  publisher = {IEEE},
  doi       = {10.1109/TE.2024.3435427},
  url       = {[http://dx.doi.org/10.1109/TE.2024.3435427](https://doi.org/10.1109/TE.2024.3435427)}
}

## License

This project is licensed under the BSD 3-Clause License - see the [LICENSE file](https://github.com/iamssgill/Q-Module-Bot?tab=BSD-3-Clause-1-ov-file#readme) for details.


