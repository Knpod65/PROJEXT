import { get, put } from "./api";
import type {
  SimpleInvigilationRates,
  SimpleInvigilationRatesPayload,
} from "@/types/invigilationSimpleRates";

export function getSimpleInvigilationRates() {
  return get<SimpleInvigilationRates>("/invigilation-payment/simple-rates");
}

export function saveSimpleInvigilationRates(body: SimpleInvigilationRatesPayload) {
  return put<SimpleInvigilationRates>("/invigilation-payment/simple-rates", body);
}

