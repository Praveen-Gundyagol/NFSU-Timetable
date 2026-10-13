from fastapi.testclient import TestClient
from ortools.sat.python import cp_model
from app.main import app

client = TestClient(app)

def test_api_health_check():
    """Verify that the FastAPI server starts and responds to health checks."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "NFSU" in data["app"]

def test_ortools_cp_sat_solver_execution():
    """Verify that Google OR-Tools CP-SAT is fully operational in our environment."""
    model = cp_model.CpModel()
    
    # Simple mathematical model: find x and y such that x + y == 10 and x != y
    num_vals = 11
    x = model.NewIntVar(0, num_vals - 1, "x")
    y = model.NewIntVar(0, num_vals - 1, "y")
    
    model.Add(x + y == 10)
    model.Add(x != y)
    
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    
    assert status == cp_model.OPTIMAL or status == cp_model.FEASIBLE
    assert solver.Value(x) + solver.Value(y) == 10
    assert solver.Value(x) != solver.Value(y)
