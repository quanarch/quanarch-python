/** The quanar and the quans answer every failure in this shape. */
export interface ApiErrorBody {
  error: { code: string; message: string; details?: { issues?: { path: string; message: string }[] } };
  request_id?: string;
}
