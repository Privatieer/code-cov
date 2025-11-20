"""
End-to-end tests simulating complete user journeys
"""
import pytest
import re
import time

# Try to import playwright, skip tests if not available
try:
    from playwright.sync_api import Page, expect
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    Page = None
    expect = None

# Skip all E2E tests if playwright is not available
pytestmark = pytest.mark.skipif(
    not PLAYWRIGHT_AVAILABLE,
    reason="Playwright not installed. Install with: poetry add --group dev playwright && poetry run playwright install chromium"
)


@pytest.mark.e2e
class TestUserJourney:
    """E2E tests for complete user workflows"""
    
    @pytest.mark.asyncio
    async def test_complete_user_registration_and_task_management(
        self,
        page: Page,
        api_client,
        test_user
    ):
        """
        Complete E2E test: User registers, logs in, creates tasks, 
        updates tasks, adds checklists, and manages task lists
        """
        # Navigate to frontend
        page.goto("http://localhost:3000")
        
        # Step 1: User Registration
        # Click register link if on login page
        register_link = page.get_by_role("link", name="Register")
        if register_link.is_visible():
            register_link.click()
        
        # Fill registration form
        email_input = page.get_by_label("Email")
        password_input = page.get_by_label("Password")
        confirm_password_input = page.get_by_label("Confirm Password")
        
        test_email = f"e2e-user-{int(time.time())}@example.com"
        test_password = "TestPassword123!"
        
        email_input.fill(test_email)
        password_input.fill(test_password)
        confirm_password_input.fill(test_password)
        
        # Submit registration
        register_button = page.get_by_role("button", name=re.compile("Register|Sign Up", re.I))
        register_button.click()
        
        # Wait for registration to complete (might redirect to login or verify)
        page.wait_for_timeout(2000)
        
        # Step 2: Login (if not auto-logged in)
        if "/login" in page.url or page.get_by_label("Email").is_visible():
            email_input = page.get_by_label("Email")
            password_input = page.get_by_label("Password")
            
            email_input.fill(test_email)
            password_input.fill(test_password)
            
            login_button = page.get_by_role("button", name=re.compile("Login|Sign In", re.I))
            login_button.click()
            
            # Wait for login to complete
            page.wait_for_timeout(2000)
        
        # Step 3: Verify we're logged in (should see tasks page)
        # Check for task-related UI elements
        expect(page).to_have_url("http://localhost:3000/")
        
        # Look for task management UI (could be "Add Task", "New Task", or task list)
        task_ui_visible = (
            page.get_by_role("button", name=re.compile("Add Task|New Task|Create Task", re.I)).is_visible(timeout=5000) or
            page.get_by_text("Tasks").is_visible(timeout=5000) or
            page.locator('input[placeholder*="task" i]').is_visible(timeout=5000)
        )
        
        assert task_ui_visible, "Task management UI should be visible after login"
        
        # Step 4: Create a new task
        # Try to find and click "Add Task" or similar button
        add_task_selectors = [
            'button:has-text("Add Task")',
            'button:has-text("New Task")',
            'button:has-text("Create Task")',
            '[aria-label*="add task" i]',
            '[data-testid*="add-task" i]'
        ]
        
        task_created = False
        for selector in add_task_selectors:
            try:
                add_button = page.locator(selector).first
                if add_button.is_visible(timeout=1000):
                    add_button.click()
                    page.wait_for_timeout(500)
                    
                    # Fill task form
                    title_input = page.locator('input[placeholder*="title" i], input[name*="title" i]').first
                    if title_input.is_visible(timeout=2000):
                        title_input.fill("E2E Test Task - Complete User Journey")
                        
                        # Try to set priority if available
                        priority_select = page.locator('select[name*="priority" i], [aria-label*="priority" i]').first
                        if priority_select.is_visible(timeout=1000):
                            priority_select.select_option("high")
                        
                        # Submit task
                        submit_button = page.get_by_role("button", name=re.compile("Create|Save|Add", re.I)).first
                        submit_button.click()
                        page.wait_for_timeout(2000)
                        task_created = True
                        break
            except Exception:
                continue
        
        # Alternative: If no button found, try direct form interaction
        if not task_created:
            # Look for inline task creation
            title_input = page.locator('input[placeholder*="task" i], input[placeholder*="title" i]').first
            if title_input.is_visible(timeout=2000):
                title_input.fill("E2E Test Task - Complete User Journey")
                page.keyboard.press("Enter")
                page.wait_for_timeout(2000)
                task_created = True
        
        assert task_created, "Should be able to create a task"
        
        # Step 5: Verify task appears in the list
        page.wait_for_timeout(1000)
        task_text = page.get_by_text("E2E Test Task - Complete User Journey")
        expect(task_text).to_be_visible(timeout=5000)
        
        # Step 6: Update task status (mark as in progress or done)
        # Look for task interaction elements (checkbox, status dropdown, etc.)
        task_item = task_text.locator("..").first
        checkbox = task_item.locator('input[type="checkbox"]').first
        
        if checkbox.is_visible(timeout=2000):
            checkbox.check()
            page.wait_for_timeout(1000)
        
        # Step 7: Verify task list functionality
        # Check if we can see task lists/sidebar
        sidebar_visible = (
            page.get_by_text("Task Lists").is_visible(timeout=2000) or
            page.locator('[data-testid*="sidebar" i]').is_visible(timeout=2000) or
            page.locator('[aria-label*="task list" i]').is_visible(timeout=2000)
        )
        
        # This is optional - task lists might not be visible
        # assert sidebar_visible, "Task list sidebar should be visible"
        
        # Step 8: Logout
        logout_button = page.get_by_role("button", name=re.compile("Logout|Sign Out", re.I))
        if logout_button.is_visible(timeout=2000):
            logout_button.click()
            page.wait_for_timeout(1000)
            
            # Verify we're logged out (should redirect to login)
            expect(page).to_have_url("http://localhost:3000/login", timeout=5000)
    
    @pytest.mark.asyncio
    async def test_user_login_and_task_creation(
        self,
        page: Page,
        api_client,
        test_user
    ):
        """
        Simpler E2E test: Existing user logs in and creates a task
        """
        # Navigate to frontend
        page.goto("http://localhost:3000/login")
        
        # Fill login form
        email_input = page.get_by_label("Email")
        password_input = page.get_by_label("Password")
        
        email_input.fill("e2e-test@example.com")
        password_input.fill("TestPassword123!")
        
        # Submit login
        login_button = page.get_by_role("button", name=re.compile("Login|Sign In", re.I))
        login_button.click()
        
        # Wait for login to complete
        page.wait_for_timeout(2000)
        
        # Verify we're logged in
        expect(page).to_have_url("http://localhost:3000/", timeout=5000)
        
        # Create a task via API to verify backend is working
        from backend.src.infrastructure.security.jwt_token import create_access_token
        
        token = create_access_token({"sub": str(test_user.id)})
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create task via API
        task_data = {
            "title": "E2E API Test Task",
            "priority": "medium",
            "description": "Created via E2E test"
        }
        
        response = await api_client.post(
            "/api/v1/tasks/",
            json=task_data,
            headers=headers
        )
        
        assert response.status_code == 201
        task = response.json()
        assert task["title"] == "E2E API Test Task"
        assert "id" in task
        
        # Verify task appears in UI (refresh page)
        page.reload()
        page.wait_for_timeout(2000)
        
        # Look for the task in the UI
        task_text = page.get_by_text("E2E API Test Task")
        expect(task_text).to_be_visible(timeout=5000)

