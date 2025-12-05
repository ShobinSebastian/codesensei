@echo off
echo ====================================
echo CodeSensei Demo Commands
echo ====================================
echo.

echo [1] Check project status
docker-compose ps
echo.

echo [2] API Health Check
curl http://localhost:8000/health
echo.

echo [3] View Metrics
curl http://localhost:8000/metrics | findstr codesensei_requests_total
echo.

echo [4] Test Analysis
curl -X POST http://localhost:8000/analyze -H "Content-Type: application/json" -d "{\"code\":\"def f(x):\n  return 10/x\n\nf(0)\",\"use_llm\":false}"
echo.

echo [5] View Logs (last 20 lines)
docker-compose logs --tail=20 codesensei-api
echo.

echo Demo complete!
pause