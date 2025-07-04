import http.server
import socketserver
import json
import urllib.parse
import uuid # For generating unique IDs for tasks

# --- In-memory Data Store (simulates a database) ---
tasks = {} # Stores tasks as {id: {title, description, status, dueDate}}

# Initial dummy data
tasks["task123"] = {
    "title": "Buy groceries",
    "description": "Milk, bread, eggs, vegetables",
    "status": "pending",
    "dueDate": "2025-06-20"
}
tasks["task456"] = {
    "title": "Finish report",
    "description": "Complete Q2 financial report",
    "status": "in-progress",
    "dueDate": "2025-06-25"
}

# --- Request Handler Class ---
class TaskAPIHandler(http.server.BaseHTTPRequestHandler):
    """
    A custom request handler for our RESTful Task Manager API.
    It processes GET, POST, PUT, PATCH, and DELETE requests.
    """

    def _set_headers(self, status_code=200, content_type='application/json'):
        """
        Helper method to set common HTTP response headers.
        Args:
            status_code (int): The HTTP status code to send.
            content_type (str): The Content-Type header value.
        """
        self.send_response(status_code)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def _read_request_body(self):
        """
        Helper method to read and parse the JSON request body.
        Returns:
            dict: Parsed JSON data, or None if there's an error.
        """
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length > 0:
            body = self.rfile.read(content_length)
            try:
                return json.loads(body.decode('utf-8'))
            except json.JSONDecodeError:
                self._set_headers(400) # Bad Request
                self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode('utf-8'))
                return None
        return {} # Return empty dict if no body (e.g., for GET, DELETE)

    # --- GET Request Handler ---
    def do_GET(self):
        """
        Handles GET requests to retrieve tasks.
        - GET /tasks: Returns all tasks.
        - GET /tasks/{id}: Returns a specific task by ID.
        """
        path_parts = [part for part in self.path.split('/') if part]

        # Case 1: GET /tasks (or just / if path_parts is empty)
        if not path_parts or (len(path_parts) == 1 and path_parts[0] == 'tasks'):
            self._set_headers(200)
            self.wfile.write(json.dumps(list(tasks.values())).encode('utf-8'))
            return

        # Case 2: GET /tasks/{id}
        if len(path_parts) == 2 and path_parts[0] == 'tasks':
            task_id = path_parts[1]
            if task_id in tasks:
                self._set_headers(200)
                self.wfile.write(json.dumps(tasks[task_id]).encode('utf-8'))
            else:
                self._set_headers(404) # Not Found
                self.wfile.write(json.dumps({"error": "Task not found"}).encode('utf-8'))
            return

        # Handle unsupported GET paths
        self._set_headers(404)
        self.wfile.write(json.dumps({"error": "Not Found"}).encode('utf-8'))

    # --- POST Request Handler ---
    def do_POST(self):
        """
        Handles POST requests to create new tasks.
        - POST /tasks: Creates a new task.
        """
        path_parts = [part for part in self.path.split('/') if part]

        if len(path_parts) == 1 and path_parts[0] == 'tasks':
            data = self._read_request_body()
            if data is None: # Error reading body
                return

            # Basic validation for required fields
            if "title" not in data:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Title is required"}).encode('utf-8'))
                return

            new_task_id = str(uuid.uuid4()) # Generate a unique ID
            new_task = {
                "id": new_task_id,
                "title": data.get("title"),
                "description": data.get("description", ""),
                "status": data.get("status", "pending"), # Default status
                "dueDate": data.get("dueDate", None)
            }
            tasks[new_task_id] = new_task

            self._set_headers(201) # 201 Created
            self.wfile.write(json.dumps(new_task).encode('utf-8'))
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not Found"}).encode('utf-8'))

    # --- PUT Request Handler ---
    def do_PUT(self):
        """
        Handles PUT requests to fully update an existing task.
        - PUT /tasks/{id}: Replaces an entire task.
        """
        path_parts = [part for part in self.path.split('/') if part]

        if len(path_parts) == 2 and path_parts[0] == 'tasks':
            task_id = path_parts[1]
            if task_id not in tasks:
                self._set_headers(404) # Not Found
                self.wfile.write(json.dumps({"error": "Task not found"}).encode('utf-8'))
                return

            data = self._read_request_body()
            if data is None: # Error reading body
                return

            # For PUT, we expect a complete replacement, so validate all core fields
            if "title" not in data or "description" not in data or "status" not in data:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "All fields (title, description, status) are required for PUT"}).encode('utf-8'))
                return

            updated_task = {
                "id": task_id, # Ensure ID remains the same
                "title": data.get("title"),
                "description": data.get("description"),
                "status": data.get("status"),
                "dueDate": data.get("dueDate", None)
            }
            tasks[task_id] = updated_task # Replace the existing task

            self._set_headers(200)
            self.wfile.write(json.dumps(updated_task).encode('utf-8'))
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not Found"}).encode('utf-8'))

    # --- PATCH Request Handler ---
    def do_PATCH(self):
        """
        Handles PATCH requests to partially update an existing task.
        - PATCH /tasks/{id}: Updates specific fields of a task (e.g., status, title).
        """
        path_parts = [part for part in self.path.split('/') if part]

        if len(path_parts) == 2 and path_parts[0] == 'tasks':
            task_id = path_parts[1]
            if task_id not in tasks:
                self._set_headers(404) # Not Found
                self.wfile.write(json.dumps({"error": "Task not found"}).encode('utf-8'))
                return

            data = self._read_request_body()
            if data is None: # Error reading body
                return

            current_task = tasks[task_id]
            # Update only the fields provided in the request body
            for key, value in data.items():
                if key in current_task: # Only update allowed fields
                    current_task[key] = value

            self._set_headers(200)
            self.wfile.write(json.dumps(current_task).encode('utf-8'))
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not Found"}).encode('utf-8'))

    # --- DELETE Request Handler ---
    def do_DELETE(self):
        """
        Handles DELETE requests to remove a task.
        - DELETE /tasks/{id}: Deletes a specific task.
        """
        path_parts = [part for part in self.path.split('/') if part]

        if len(path_parts) == 2 and path_parts[0] == 'tasks':
            task_id = path_parts[1]
            if task_id in tasks:
                del tasks[task_id]
                self._set_headers(204) # 204 No Content (successful deletion, no response body)
            else:
                self._set_headers(404) # Not Found
                self.wfile.write(json.dumps({"error": "Task not found"}).encode('utf-8'))
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not Found"}).encode('utf-8'))

# --- Server Setup ---
PORT = 8000
Handler = TaskAPIHandler

# Create a simple HTTP server
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving Task Manager API at port {PORT}")
    print("To test, use tools like curl or Postman, or your browser.")
    print("Example Endpoints:")
    print("  GET    http://localhost:8000/tasks")
    print("  GET    http://localhost:8000/tasks/task123")
    print("  POST   http://localhost:8000/tasks (with JSON body)")
    print("  PUT    http://localhost:8000/tasks/task123 (with JSON body)")
    print("  PATCH  http://localhost:8000/tasks/task123 (with JSON body)")
    print("  DELETE http://localhost:8000/tasks/task123")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        httpd.shutdown()