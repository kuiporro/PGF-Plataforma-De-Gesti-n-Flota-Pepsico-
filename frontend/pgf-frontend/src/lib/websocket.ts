/**
 * Cliente WebSocket para notificaciones en tiempo real.
 * 
 * Maneja la conexión WebSocket con el servidor para recibir
 * notificaciones en tiempo real sin necesidad de polling.
 */

export class NotificationWebSocket {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private pingInterval: NodeJS.Timeout | null = null;
  private listeners: Map<string, Set<(data: any) => void>> = new Map();

  constructor(private getToken: () => Promise<string | null>) {}

  /**
   * Conecta al servidor WebSocket.
   */
  async connect(): Promise<void> {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      return; // Ya está conectado
    }

    try {
      const token = await this.getToken();
      if (!token) {
        // No mostrar error si simplemente no hay token (usuario no autenticado)
        // Solo loguear en modo debug
        console.debug("WebSocket: No hay token disponible, omitiendo conexión");
        return;
      }

      // Construir URL del WebSocket
      // En desarrollo, usar localhost:8000 para el backend
      // En producción, usar la misma URL del backend
      const wsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:";
      const wsHost = process.env.NEXT_PUBLIC_WS_URL || 
                     (process.env.NODE_ENV === "development" ? "localhost:8000" : window.location.host);
      const wsUrl = `${wsProtocol}//${wsHost}/ws/notifications/?token=${token}`;

      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        console.log("WebSocket conectado");
        this.reconnectAttempts = 0;
        this.startPing();
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.handleMessage(data);
        } catch (error) {
          console.error("Error al parsear mensaje WebSocket:", error);
        }
      };

      this.ws.onerror = (error) => {
        console.error("Error en WebSocket:", error);
      };

      this.ws.onclose = () => {
        console.log("WebSocket desconectado");
        this.stopPing();
        this.attemptReconnect();
      };
    } catch (error) {
      console.error("Error al conectar WebSocket:", error);
      this.attemptReconnect();
    }
  }

  /**
   * Desconecta del servidor WebSocket.
   */
  disconnect(): void {
    this.stopPing();
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  /**
   * Suscribe a eventos de notificaciones.
   */
  on(event: string, callback: (data: any) => void): () => void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event)!.add(callback);

    // Retornar función para desuscribirse
    return () => {
      this.listeners.get(event)?.delete(callback);
    };
  }

  /**
   * Maneja mensajes recibidos del servidor.
   */
  private handleMessage(data: any): void {
    const { type, notification } = data;

    if (type === "notification" && notification) {
      // Emitir evento de nueva notificación
      this.emit("notification", notification);
    } else if (type === "connection_established") {
      console.log("Conexión WebSocket establecida");
    } else if (type === "pong") {
      // Respuesta a ping, conexión viva
    }
  }

  /**
   * Emite un evento a todos los listeners.
   */
  private emit(event: string, data: any): void {
    const listeners = this.listeners.get(event);
    if (listeners) {
      listeners.forEach((callback) => {
        try {
          callback(data);
        } catch (error) {
          console.error("Error en listener de WebSocket:", error);
        }
      });
    }
  }

  /**
   * Intenta reconectar al servidor.
   */
  private attemptReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error("Máximo de intentos de reconexión alcanzado");
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);

    console.log(`Reintentando conexión en ${delay}ms (intento ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);

    setTimeout(() => {
      this.connect();
    }, delay);
  }

  /**
   * Inicia el ping periódico para mantener la conexión viva.
   */
  private startPing(): void {
    this.pingInterval = setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({ type: "ping" }));
      }
    }, 30000); // Ping cada 30 segundos
  }

  /**
   * Detiene el ping periódico.
   */
  private stopPing(): void {
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
      this.pingInterval = null;
    }
  }
}

