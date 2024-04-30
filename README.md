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

- There is a direct link to Heroku here, in the report and in the supporting materials: https://vast-journey-85249-5fa42e95d1f8.herokuapp.com/




