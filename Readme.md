<div align="center">

  <img alt="Logo" src="./vertigo-ui/src/assets/logo.svg" style="width: 10%" />
  <h3 align="center">Vertigo</h3>

  <p align="center">
    Vertigo is a web app designed to help you organize, manage, and track your comic book collection with ease. Created using <a href="https://vuejs.org/">Vue.js</a> and <a href="https://flask.palletsprojects.com/en/3.0.x/">Flask</a>
    <br />
    <br />
  </p>
 
  <p align='center'>
<img alt="Vertigo Homepage Screenshot" src="./.github/images/screenshot.png" style="width: 90%" />
</p>
 <br />
 <br />
</div>

> **⚠ Disclaimer ⚠**: Vertigo is WIP and under active development. Expect occasional bugs, incomplete features, and potential breaking changes as I add new features and improve functionality. Only the basic CRUD is done till now.

## Goals:
- [x] A responsive modern web app to track and curate physical comicbook collection
- [x] Search and filter options based on various criteria such as title, publisher etc.
- [x] Track reading progress (read/unread, backlog and ratings if needed).
- [x] Generate insightful statistics on collection.
- [ ] Explore options to integrate with external APIs for automatic fetching of details.
- [ ] Backup/Export User Data to commonly used formats.

Feel free to reach out if you have anything else you'd like to see!

## Getting Started:
Vertigo is not released yet, and is under active development, but if you can try it out using the Developer Guide below.
<br/>
<br/>

## Developer Guide:

#### Prerequisites:

- Python 3 (https://www.python.org/downloads/)
- Node.js and npm (https://nodejs.org/)

### Clone the repository

```bash
git clone https://github.com/anonhacker47/vertigo-comic-collection -b main
cd vertigo-comic-collection
```

### Setup
Set up a Python 3 virtualenv and install the dependencies on it:

```bash
cd vertigo-backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
Create the db and run flask app:

```bash
alembic upgrade head
flask run
```
By default, You can try out the app from http://localhost:5000/ .
<br/>
<br/>

> If you want to tinker with the Frontend follow the below instructions.

#### Frontend Setup
Install the dependencies:
```bash
cd vertigo-ui
npm install
```
Run the Vue.js frontend:
```bash
npm run dev
```
Voila! you can find the frontend at http://localhost:5173/

<br/>

## Acknowledgements

- **[Miguel Grinberg Microblog API](https://github.com/miguelgrinberg/microblog-api)**
