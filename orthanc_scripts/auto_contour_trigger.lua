-- auto_contour.lua

function OnStoredInstance(instanceId, tags, metadata, origin)
  -- Log the instance ID
  print("Lua says: OnStoredInstance called with instanceId: " .. instanceId)

  -- Prepare JSON payload for POST
  local payload = {
    instance_id = instanceId
  }

  -- Encode payload to JSON
  local jsonPayload = OrthancLuaJson.encode(payload)

  -- Log payload for debugging
  print("Lua says: JSON payload: " .. jsonPayload)

  -- Perform POST to MONAI auto-contour endpoint
  local httpResponse, httpStatus = RestApiPost(
    "http://monai:8000/auto_contour",
    jsonPayload,
    { ["Content-Type"] = "application/json" }
  )

  if httpStatus == 200 then
    print("Lua says: Successfully triggered auto-contour job for instance: " .. instanceId)
  else
    print("Lua says: Failed to trigger auto-contour for instance: " .. instanceId .. ", HTTP status: " .. tostring(httpStatus))
  end
end
