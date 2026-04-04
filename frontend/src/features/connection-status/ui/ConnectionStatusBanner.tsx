interface ConnectionStatusBannerProps {
  online: boolean;
  transport: string;
}

export function ConnectionStatusBanner({
  online,
  transport
}: ConnectionStatusBannerProps) {
  return (
    <div className={`connection-banner ${online ? "is-online" : "is-offline"}`}>
      <span className="connection-indicator" />
      <div>
        <strong>{online ? "Live stream connected" : "Connection lost"}</strong>
        <p>{transport}</p>
      </div>
    </div>
  );
}
