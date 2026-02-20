import React, { useState } from 'react';
import './Results.css';

function Results({ results }) {
  const [activeTab, setActiveTab] = useState('fish');

  const { fish, recipes } = results;

  return (
    <div className="results">
      <h2>Your Progress</h2>

      <div className="tabs">
        <button
          className={`tab ${activeTab === 'fish' ? 'active' : ''}`}
          onClick={() => setActiveTab('fish')}
        >
          Fish ({fish.caught}/{fish.total})
        </button>
        <button
          className={`tab ${activeTab === 'recipes' ? 'active' : ''}`}
          onClick={() => setActiveTab('recipes')}
        >
          Recipes ({recipes.cooked}/{recipes.total})
        </button>
      </div>

      <div className="tab-content">
        {activeTab === 'fish' && (
          <div className="fish-section">
            <div className="stats">
              <div className="stat">
                <span className="stat-label">Total Fish:</span>
                <span className="stat-value">{fish.total}</span>
              </div>
              <div className="stat">
                <span className="stat-label">Caught:</span>
                <span className="stat-value">{fish.caught}</span>
              </div>
              <div className="stat">
                <span className="stat-label">Missing:</span>
                <span className="stat-value">{fish.uncaught}</span>
              </div>
            </div>

            {fish.missingList.length > 0 ? (
              <>
                <h3>Missing Fish ({fish.uncaught})</h3>
                <ul className="item-list">
                  {fish.missingList.map((fishItem) => (
                    <li key={fishItem.id} className="item">
                      {fishItem.name}
                    </li>
                  ))}
                </ul>
              </>
            ) : (
              <div className="completion-message">
                <h3>Congratulations!</h3>
                <p>You've caught all the fish!</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'recipes' && (
          <div className="recipes-section">
            <div className="stats">
              <div className="stat">
                <span className="stat-label">Total Recipes:</span>
                <span className="stat-value">{recipes.total}</span>
              </div>
              <div className="stat">
                <span className="stat-label">Learned:</span>
                <span className="stat-value">{recipes.learned}</span>
              </div>
              <div className="stat">
                <span className="stat-label">Cooked:</span>
                <span className="stat-value">{recipes.cooked}</span>
              </div>
              <div className="stat">
                <span className="stat-label">Need to Cook:</span>
                <span className="stat-value">{recipes.missingToCook}</span>
              </div>
            </div>

            {recipes.missingList.length > 0 ? (
              <>
                <h3>Recipes to Cook ({recipes.missingToCook})</h3>
                <ul className="item-list recipes">
                  {recipes.missingList.map((recipe) => (
                    <li key={recipe.name} className="item recipe-item">
                      <div className="recipe-header">
                        <span className="recipe-name">{recipe.name}</span>
                        {recipe.needToLearn && (
                          <span className="need-to-learn-badge">Need to Learn</span>
                        )}
                      </div>
                      <div className="ingredients">
                        <span className="ingredients-label">Ingredients:</span>
                        <span className="ingredients-list">
                          {recipe.ingredients.map((ing, idx) => (
                            <span key={idx}>
                              {ing.quantity}x {ing.name}
                              {idx < recipe.ingredients.length - 1 ? ', ' : ''}
                            </span>
                          ))}
                        </span>
                      </div>
                    </li>
                  ))}
                </ul>
              </>
            ) : (
              <div className="completion-message">
                <h3>Congratulations!</h3>
                <p>You've cooked all the recipes!</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default Results;
