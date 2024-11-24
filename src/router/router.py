import csv
from datetime import datetime
from typing import List

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from pydantic import BaseModel
import os

from sqlalchemy import text
from sqlalchemy.orm import Session

from src.database import get_my_db, get_sid_db
from src.http_models import DetailedResponse
from src.queries import query_grades, query_personal, query_courses

router = APIRouter(prefix="/predictionsController")


class YearsRequest(BaseModel):
    years: List[str]


def save_data_to_csv(data, year):
    # Define the file name for the CSV file for the specific year
    filename = f"student_data_{year}.csv"

    # Ensure there is data to save
    if not data:
        print(f"No data available for year {year}, skipping file creation.")
        return

    # Write headers to the CSV file (personal data + subjects)
    fieldnames = list(data[0].keys())  # Use the keys from the first record for column names

    try:
        with open(filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            writer.writeheader()  # Write the header
            writer.writerows(data)  # Write all data rows

        print(f"Data successfully saved to {filename}")
        return filename
    except Exception as e:
        print(f"Error saving data to CSV for year {year}: {e}")
        return "Error saving data to CSV for year {year}"


def retrieve_student_data_for_year(year: str, db: Session):
    # Execute the first query for grades
    grades_query = str(query_grades).replace("{years_placeholder}", year)
    grades_results = db.execute(text(grades_query)).mappings().fetchall()
    print("Columns in grades_results:", grades_results[0].keys() if grades_results else "No data")

    # Format grades data and collect unique subjects
    grades_data = {}
    subjects = set()
    for row in grades_results:
        tr_id = row["tr_id"]
        if tr_id not in grades_data:
            grades_data[tr_id] = {}
        grades_data[tr_id][row["nazwa"]] = row["punkty"]
        subjects.add(row["nazwa"])

    # Execute the second query for personal data
    personal_query = str(query_personal).replace("{years_placeholder}", year)
    personal_results = db.execute(text(personal_query)).mappings().fetchall()
    print("Columns in personal_results:", personal_results[0].keys() if personal_results else "No data")

    # Combine grades and personal data for the given year
    year_data = []
    for person in personal_results:
        if str(person["tr_zmiana"])[:4] == str(year):  # Filter by the year parameter
            tr_id = person["tr_id"]
            person_data = {key: person[key] for key in person.keys()}
            grades = grades_data.get(tr_id, {})

            # Add grades as separate fields, default to 0 if no grade is found
            for subject in subjects:
                person_data[subject] = grades.get(subject, 0)

            year_data.append(person_data)

    return year_data


@router.post("/retrieve_students_data_and_save", tags=["predictionsController"], response_model=DetailedResponse)
async def retrieve_student_data(request: YearsRequest, db: Session = Depends(get_sid_db)) -> DetailedResponse:
    try:
        # Extract years from the request
        years: List[str] = request.years

        response_file_names = []
        for year in years:
            year_data = retrieve_student_data_for_year(year, db)

            # Save the data for the current year to a CSV file
            response_file_names.append(save_data_to_csv(year_data, year))

        return DetailedResponse(code=200, message="Data retrieved successfully", data=response_file_names)

    except Exception as e:
        db.rollback()
        print(f"Error occurred while retrieving data: {e}")
        raise HTTPException(status_code=500, detail="Error occurred while retrieving data")


@router.post("/retrieve_students_data", tags=["predictionsController"], response_model=DetailedResponse)
async def retrieve_student_data(year: str, db: Session = Depends(get_sid_db)) -> DetailedResponse:
    try:
        # Retrieve student data for the given year
        year_data = retrieve_student_data_for_year(year, db)

        return DetailedResponse(code=200, message="Data retrieved successfully", data=year_data)

    except Exception as e:
        db.rollback()
        print(f"Error occurred while retrieving data: {e}")
        raise HTTPException(status_code=500, detail="Error occurred while retrieving data")


@router.post("/retrieve_courses_data", tags=["predictionsController"], response_model=DetailedResponse)
async def retrieve_courses_data(db: Session = Depends(get_sid_db)) -> DetailedResponse:
    """
    Endpoint to retrieve and process courses data from the database.

    Args:
        db (Session): Database session injected using FastAPI Depends.

    Returns:
        DetailedResponse: A response model containing the processed data.
    """
    try:
        processed_data = await extract_courses(db)

        # Convert processed data back to a list of dictionaries for JSON response
        processed_data_dict = processed_data.to_dict(orient="records")

        # Prepare and return the response
        return DetailedResponse(
            code=200,
            message="Data processed and retrieved successfully",
            data=processed_data_dict
        )

    except Exception as e:
        db.rollback()  # Roll back any transaction if an error occurs
        print(f"Error occurred while processing courses data: {e}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing courses data"
        )


async def extract_courses(db):
    courses_query = str(query_courses)
    courses_results = db.execute(text(courses_query)).mappings().fetchall()
    import pandas as pd
    data = pd.DataFrame(courses_results)
    data['kk_nazwa'] = data['kk_nazwa'].str.strip()
    # Process data: group by KK_NAZWA, aggregate KK_ID into lists, and determine most common WD_NAZWA
    processed_data = (
        data.groupby("kk_nazwa")
        .agg({
            "kk_id": list,
            "wd_nazwa": lambda x: x.mode()[0] if not x.mode().empty else None
        })
        .reset_index()
    )
    return processed_data




@router.post("/save_courses_data", tags=["predictionsController"])
async def save_courses_data(db: Session = Depends(get_sid_db)) -> dict:
    """
    Endpoint to retrieve, process, and save courses data to a CSV file.

    Args:
        db (Session): Database session injected using FastAPI Depends.

    Returns:
        dict: A dictionary containing the name of the saved file.
    """
    try:
        processed_data = await extract_courses(db)
        output_dir = "output_files"
        os.makedirs(output_dir, exist_ok=True)
        file_name = f"courses_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        file_path = os.path.join(output_dir, file_name)
        processed_data.to_csv(file_path, index=False)

        return {"file_name": file_name}

    except Exception as e:
        db.rollback()  # Roll back any transaction if an error occurs
        print(f"Error occurred while saving courses data: {e}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while saving courses data"
        )
