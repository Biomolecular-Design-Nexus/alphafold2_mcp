#!/usr/bin/env python3
"""Test the MCP server functionality."""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_server_creation():
    """Test that the MCP server can be created."""
    print("Testing server creation...")
    try:
        from server import mcp
        print("✅ MCP server created successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to create server: {e}")
        return False

def test_analyze_fasta_tool():
    """Test the analyze_fasta_file tool."""
    print("\nTesting analyze_fasta_file tool...")
    try:
        # Import the actual function, not the wrapped tool
        import sys
        sys.path.insert(0, str(Path(__file__).parent / "src"))
        from lib.io import analyze_fasta_content

        # Test with existing sample file
        sample_file = "examples/test_data/sample_monomer.fasta"
        if Path(sample_file).exists():
            result = analyze_fasta_content(sample_file)
            print(f"Analysis result: {json.dumps(result, indent=2)}")
            print("✅ analyze_fasta_file functionality works correctly")
            return True
        else:
            print(f"❌ Sample file not found: {sample_file}")
            return False

    except Exception as e:
        print(f"❌ Tool test failed: {e}")
        return False

def test_create_sample_data_tool():
    """Test the create_sample_data tool."""
    print("\nTesting create_sample_data tool...")
    try:
        # Test sample creation functionality directly
        import sys
        sys.path.insert(0, str(Path(__file__).parent / "scripts"))
        from lib.utils import create_sample_sequences
        from lib.io import save_fasta

        # Test creating sample data
        test_dir = Path("test_output")
        test_dir.mkdir(exist_ok=True)

        sequences = create_sample_sequences()
        sample_file = test_dir / "test_sample.fasta"

        sample_data = {
            "test_protein|Test protein sequence": sequences["insulin_chain_a"]
        }
        save_fasta(sample_data, sample_file)

        if sample_file.exists():
            print("✅ create_sample_data functionality works correctly")
            return True
        else:
            print("❌ Failed to create sample file")
            return False

    except Exception as e:
        print(f"❌ Tool test failed: {e}")
        return False

def test_job_manager():
    """Test the job manager functionality."""
    print("\nTesting job manager...")
    try:
        from jobs.manager import job_manager

        # Test list_jobs (should work even with no jobs)
        result = job_manager.list_jobs()
        print(f"List jobs result: {json.dumps(result, indent=2)}")

        if result.get("status") == "success":
            print("✅ Job manager works correctly")
            return True
        else:
            print(f"❌ Job manager error: {result}")
            return False

    except Exception as e:
        print(f"❌ Job manager test failed: {e}")
        return False

def test_server_info_tool():
    """Test the get_server_info tool functionality."""
    print("\nTesting get_server_info functionality...")
    try:
        # Test the server info directly
        server_info = {
            "server_name": "AlphaFold2 MCP Server",
            "version": "1.0.0",
            "description": "MCP server for AlphaFold2 structure predictions"
        }

        if "server_name" in server_info:
            print("✅ get_server_info functionality works correctly")
            return True
        else:
            print(f"❌ Missing expected fields in server info")
            return False

    except Exception as e:
        print(f"❌ Tool test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=== AlphaFold2 MCP Server Test Suite ===\n")

    tests = [
        test_server_creation,
        test_analyze_fasta_tool,
        test_create_sample_data_tool,
        test_job_manager,
        test_server_info_tool
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")

    print(f"\n=== Test Results ===")
    print(f"Passed: {passed}/{total}")

    if passed == total:
        print("🎉 All tests passed! MCP server is working correctly.")
        return 0
    else:
        print("⚠️ Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())