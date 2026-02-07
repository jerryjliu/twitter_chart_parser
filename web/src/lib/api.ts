import type {
  ParseTweetRequest,
  ParseTweetResponse,
  ValidateLlamaKeyResponse,
} from "@/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function parseErrorMessage(response: Response): Promise<string> {
  try {
    const payload = (await response.json()) as { message?: string; detail?: string };
    return payload.message || payload.detail || "Request failed";
  } catch {
    return "Request failed";
  }
}

export async function validateLlamaKey(apiKey: string): Promise<ValidateLlamaKeyResponse> {
  const response = await fetch(`${API_BASE_URL}/validate-llama-key`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ api_key: apiKey }),
  });

  if (!response.ok) {
    throw new Error(await parseErrorMessage(response));
  }

  return (await response.json()) as ValidateLlamaKeyResponse;
}

export async function parseTweet(payload: ParseTweetRequest): Promise<ParseTweetResponse> {
  const response = await fetch(`${API_BASE_URL}/parse-tweet`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(await parseErrorMessage(response));
  }

  return (await response.json()) as ParseTweetResponse;
}

export async function extractTweetImages(tweetUrl: string, xBearerToken?: string): Promise<{ image_urls: string[] }> {
  const response = await fetch(`${API_BASE_URL}/extract-tweet-images`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ tweet_url: tweetUrl, x_bearer_token: xBearerToken }),
  });

  if (!response.ok) {
    throw new Error(await parseErrorMessage(response));
  }

  return (await response.json()) as { image_urls: string[] };
}
