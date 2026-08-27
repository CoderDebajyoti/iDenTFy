function ResultCard({
  icon,
  title,
  status,
  value,
  description,
}) {
  const statusText = {
    passed: "Passed",
    skipped: "Skipped",
    failed: "Failed",
  };

  return (
    <div className="result-card">

      <div className="result-card-top">

        <div className="result-card-icon">
          {icon}
        </div>

        <span className={`status-pill ${status}`}>
          {status === "passed" && "✓ "}
          {status === "failed" && "✕ "}
          {status === "skipped" && "— "}

          {statusText[status]}
        </span>

      </div>


      <h3>
        {title}
      </h3>


      <strong className="result-value">
        {value}
      </strong>


      <p>
        {description}
      </p>

    </div>
  );
}

export default ResultCard;