// src/lib/api.server.ts
import axios from "axios";
import { getServerAuthHeader } from "./cookies.server";
import { API_BASE } from "./constants";

export function serverApi() {
  return axios.create({
    baseURL: API_BASE,
    headers: getServerAuthHeader(),
  });
}
