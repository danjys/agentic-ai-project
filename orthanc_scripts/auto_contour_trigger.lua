print("auto_contour_trigger.lua loaded")

function OnStoredInstance(instanceId)
    print("OnStoredInstance called with instanceId: " .. instanceId)

    local http = require 'socket.http'
    local ltn12 = require 'ltn12'
    local url = "http://agent:8000/auto_contour"
    local body = "instance_id=" .. instanceId
  
    local response_body = {}
  
    local res, code, response_headers = http.request{
      url = url,
      method = "POST",
      headers = {
        ["Content-Type"] = "application/x-www-form-urlencoded",
        ["Content-Length"] = tostring(#body)
      },
      source = ltn12.source.string(body),
      sink = ltn12.sink.table(response_body)
    }
  
    if code == 200 then
      print("Auto-contour triggered for instance: " .. instanceId)
    else
      print("Failed to trigger auto-contour for instance: " .. instanceId .. ", HTTP code: " .. tostring(code))
    end
end
