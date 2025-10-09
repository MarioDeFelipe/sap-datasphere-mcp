#!/usr/bin/env python3
"""
Fix the Glue Tables button - same issue as Explore Products
"""

import urllib.request
import boto3
import json
import zipfile
import io
import time
from datetime import datetime

def debug_glue_tables_function():
    """Debug the Glue Tables button function"""
    
    print("🔍 DEBUGGING GLUE TABLES BUTTON")
    print("=" * 40