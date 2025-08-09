-- Extend package.path so require can find json.lua here
package.path = package.path .. ";/etc/orthanc/lua/?.lua"

local json = require("json")

function OnStoredInstance(instanceId)
    print("Lua says: OnStoredInstance called with instanceId: " .. instanceId)

    -- Compose payload table
    local payload = {
        instance_id = instanceId
    }

    -- Encode payload to JSON string
    local payloadJson = json.encode(payload)

    -- Post to your FastAPI endpoint
    local url = "http://monai-service:8000/auto_contour"

    -- Use Orthanc RestApiPost for HTTP POST with JSON content
    local status, response = pcall(function()
        return RestApiPost(url, payloadJson, "application/json")
    end)

    if not status or not response then
        print("Lua says: Failed to trigger auto-contour, HTTP status: nil")
        return
    end

    print("Lua says: auto-contour triggered successfully. Response: " .. response)
end

print("Lua says: auto_contour_trigger.lua loaded")
