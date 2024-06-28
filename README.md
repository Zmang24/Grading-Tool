Grader Application
The Grader Application is a desktop application built using Python and Tkinter, with additional styling from the ttkbootstrap library. It allows users to manage trainee grading data efficiently. The app supports functionalities such as logging in with a PIN, importing answer keys and trainee submissions, grading submissions, displaying results, and exporting results to Excel files.

Features
User Authentication: Login using a secure PIN.
Data Import: Import answer keys and trainee submissions from Excel files.
Automatic Grading: Automatically grade submissions based on the imported answer key.
View Results: Display grading results within the application.
Export Results: Export trainee-specific results or all results to Excel files.
Installation
Clone the repository:

bash
Copy code
git clone https://github.com/yourusername/grader-app.git
cd grader-app
Install dependencies:
Make sure you have Python installed. Then, install the required Python libraries:

bash
Copy code
pip install tkinter ttkbootstrap pandas
Run the application:

bash
Copy code
python Grader.py
Usage
Login: Start the application and enter the PIN to access the main interface.
Import Answer Key: Click on 'Import Key' to upload an Excel file containing the answer key.
Import Trainee Submissions: Click on 'Import Trainee Submission' to upload an Excel file with trainee answers.
Grade Submissions: Click on 'Grade' to automatically grade the imported submissions.
View Results: Use the 'Display Results' button to view all graded results within the app.
Export Results:
To export results for a specific trainee, enter the trainee's name, date, and exercise, then click on 'Export Trainee Result'.
To export all results, simply click on 'Export All Results'.
File Structure
Grader.py: The main application script containing all the logic and UI components.
database.db: SQLite database file where the grading results are stored (automatically created).
