import requests
import time

BASE_URL = "https://qa-testing-navy.vercel.app"
STATIC_ID = "sit24it031"
CANDIDATE_ID = f"{STATIC_ID}_{int(time.time())}"

HEADERS = {
    "X-Candidate-ID": CANDIDATE_ID,
    "Content-Type": "application/json"
}

def authenticate(session):
    """Acquires a valid Bearer token using our persistent Candidate ID."""
    auth_url = f"{BASE_URL}/api/auth"
    try:
        response = session.post(auth_url)
        if response.status_code in [200, 201]:
            auth_data = response.json()
            token = auth_data.get("token") or auth_data.get("sessionToken")
            if token:
                session.headers.update({"Authorization": f"Bearer {token}"})
                return True
    except Exception as e:
        print(f"       🚨 Auth exception: {e}")
    return False

def run_automation_test():
    session = requests.Session()
    session.headers.update(HEADERS)
    
    video_id = None
    
    try:
        print("\n🔐 Phase 1: Authenticating with server...")
        if not authenticate(session):
            print("❌ Initial Authentication Failed!")
            return
        print("✅ Authentication Successful! Token retrieved.")


        print("\n📹 Phase 2: Registering a new video record...")
        video_url = f"{BASE_URL}/api/videos"
        video_payload = {
            "title": "Internship Automation Test Video",
            "description": "Validating the end-to-end caption lifecycle."
        }
        create_response = session.post(video_url, json=video_payload)
        
        if create_response.status_code in [200, 201]:
            video_data = create_response.json()
            video_id = video_data.get("id") or video_data.get("data", {}).get("id")
            print(f"✅ Video Record Created! Tracked ID: {video_id}")
        else:
            print(f"❌ Failed to create video record! Status code: {create_response.status_code}")
            return


        print(f"\n⚙️ Phase 3: Triggering caption rendering pipeline for Video {video_id}...")
        process_url = f"{BASE_URL}/api/videos/{video_id}/process-captions"
        process_response = session.post(process_url)
        
        if process_response.status_code in [200, 202]:
            print("✅ Caption engine triggered successfully.")
            print("⏳ Monitoring live processing status...")
            
            is_processed = False

            for attempt in range(30):
                status_response = session.get(f"{BASE_URL}/api/videos/{video_id}")
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    status = status_data.get("status") or status_data.get("data", {}).get("status")
                    print(f"   [Check {attempt + 1}/30] Current Status: {status}")
                    
                    if status in ["completed", "processed"]:
                        print("✅ Video captioning process complete!")
                        is_processed = True
                        break
                elif status_response.status_code == 401:
                    print(f"   [Check {attempt + 1}/30] ❌ Token Expired (401). Execution halted.")
                    break
                else:
                    print(f"   [Check {attempt + 1}/30] ❌ Status check unexpected code: {status_response.status_code}")
            
            if is_processed:
                print("\n📝 Fetching raw generated caption texts...")
                caption_response = session.get(f"{BASE_URL}/api/captions?videoId={video_id}")
                if caption_response.status_code == 200:
                    print(f"✅ Captions Received: {caption_response.text}")
                else:
                    print(f"⚠️ Captions endpoint returned error status: {caption_response.status_code}")
        else:
            print(f"❌ Failed to start caption engine! Status code: {process_response.status_code}")

    except Exception as e:
        print(f"\n🚨 Exception intercepted during runtime execution: {e}")
        
    finally:
        if video_id:
            print(f"\n🧹 Phase 4: Commencing database cleanup for Video {video_id}...")
            delete_url = f"{BASE_URL}/api/videos/{video_id}"
            delete_response = session.delete(delete_url)
            if delete_response.status_code in [200, 204]:
                print("✅ Database Teardown Complete! Environment is clean.")
            else:
                print(f"⚠️ Clean up warning: Removal failed with status {delete_response.status_code}")
        else:
            print("\n🧹 Phase 4 skipped: No items were registered to clear out.")


if __name__ == "__main__":
    run_automation_test()
