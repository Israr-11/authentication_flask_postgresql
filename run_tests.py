import os
import sys
import subprocess
from datetime import datetime

def run_tests():
    """Run tests and generate reports"""
    
    # CREATE REPORTS DIRECTORY IF IT DOESN'T EXIST
    os.makedirs('test_reports', exist_ok=True)
    
    # GENERATE TIMESTAMP FOR REPORT
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # DEFINE REPORT PATHS
    test_report = f'test_reports/unit-tests-{timestamp}.html'
    coverage_report = 'test_reports/coverage'
    
    print("=" * 60)
    print("RUNNING UNIT TESTS")
    print("=" * 60)
    
    # RUN PYTEST WITH COVERAGE AND HTML REPORT
    cmd = [
        'pytest',
        'tests/unit/',
        '-v',
        '--cov=.',
        '--cov-report=html:' + coverage_report,
        '--cov-report=term-missing',
        '--html=' + test_report,
        '--self-contained-html'
    ]
    
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print(f"\n📊 Test Report: {test_report}")
        print(f"📈 Coverage Report: {coverage_report}/index.html")
        
        # OPEN REPORTS IN BROWSER (WINDOWS)
        print("\nOpening reports in browser...")
        os.system(f'start {test_report}')
        os.system(f'start {coverage_report}/index.html')
    else:
        print("\n" + "=" * 60)
        print("❌ SOME TESTS FAILED!")
        print("=" * 60)
        print(f"\n📊 Test Report: {test_report}")
        
        # STILL OPEN REPORT TO SEE FAILURES
        os.system(f'start {test_report}')
    
    return result.returncode

if __name__ == '__main__':
    sys.exit(run_tests())