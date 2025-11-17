import { NextResponse } from "next/server";

/**
 * Safely parses JSON from a fetch Response
 * Handles empty responses and invalid JSON gracefully
 */
export async function safeJsonParse(response: Response): Promise<any> {
  const text = await response.text();
  
  // Handle empty responses
  if (!text || text.trim() === "") {
    if (!response.ok) {
      return { detail: "Empty response from backend" };
    }
    return {};
  }
  
  try {
    return JSON.parse(text);
  } catch (e) {
    console.error("Invalid JSON response:", text.substring(0, 200));
    return { 
      detail: "Invalid JSON response from backend", 
      raw: text.substring(0, 200) 
    };
  }
}

/**
 * Helper to handle backend fetch responses with proper error handling
 */
export async function handleBackendResponse(response: Response): Promise<NextResponse> {
  const data = await safeJsonParse(response);
  
  // If JSON parsing failed, return error
  if (data.detail && data.detail.includes("Invalid JSON")) {
    return NextResponse.json(data, { status: response.status || 500 });
  }
  
  return NextResponse.json(data, { status: response.status });
}

