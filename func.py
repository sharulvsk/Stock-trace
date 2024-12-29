import psycopg2
from psycopg2 import OperationalError
import random
import pdfplumber
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from connection import get_connection

def validate_user(username, password):
    if username == "admin@gmail.com" and password == "pass":
        return True
    elif username == "user@gmail.com" and password == "pass":
        return True
    return False

