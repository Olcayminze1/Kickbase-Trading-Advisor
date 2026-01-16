def split_data(df, features, target, test_size=0.2, random_state=42):
    """
    Splits the dataframe into train and test sets.
    IMPORTANT: X and y must have the exact same number of rows.
    """

    from sklearn.model_selection import train_test_split

    # Keep only the needed columns and drop rows where ANY of them is missing
    df = df[features + [target]].dropna().copy()

    X = df[features]
    y = df[target]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        shuffle=True,
    )

    return X_train, X_test, y_train, y_test
