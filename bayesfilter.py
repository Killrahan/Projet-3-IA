import numpy as np
from scipy.stats import binom

from pacman_module.game import Agent, Directions, manhattanDistance


def gridSize(grid):
    n_x = 0
    n_y = 0

    for x in grid:
        n_x += 1

    for x in grid[0]:
        n_y += 1

    return (n_x, n_y)

class BeliefStateAgent(Agent):
    """Belief state agent.

    Arguments:
        ghost: The type of ghost (as a string).
    """

    def __init__(self, ghost):
        super().__init__()

        self.ghost = ghost

    def transition_matrix(self, walls, position):
        """Builds the transition matrix

            T_t = P(X_t | X_{t-1})

        given the current Pacman position.

        Arguments:
            walls: The W x H grid of walls.
            position: The current position of Pacman.

        Returns:
            The W x H x W x H transition matrix T_t. The element (i, j, k, l)
            of T_t is the probability P(X_t = (k, l) | X_{t-1} = (i, j)) for
            the ghost to move from (i, j) to (k, l).
        """

        #def computeProba(i,j,k,l) :
        
        print(walls)
            
        W,H = gridSize(walls)
        
        trans = np.ndarray((W,H,W,H))
        
        for i in range(W-1) :
            for j in range(H-1) :
                
                print(i,j)
                
                toModify = []
                
                nbTrans = 4 #nbr of possible transitions
                
                if walls[i - 1][j]: 
                    nbTrans -= 1
                else:
                    toModify += [(i-1, j)] 
                
                if walls[i][j - 1]:
                    nbTrans -= 1
                else:
                    toModify += [(i, j-1)]
                    
                if walls[i + 1][j]:
                    nbTrans -= 1
                else:
                    toModify += [(i+1, j)]
                    
                if walls[i][j + 1]:
                    nbTrans -= 1
                else:
                    toModify += [(i, j + 1)]
                    
                if nbTrans == 0:
                    trans[i][j][i][j] = 1 #ghost blocked
                    
                else:
                    for k,l in toModify:
                        trans[i][j][k][l] = 1/nbTrans #we assume here that the ghosts move randomly
                    """
                    To compute the actual probability of the positions, use the fact that the ghosts favorize a given discplacement
                    """

        return trans

    def observation_matrix(self, walls, evidence, position):
        """Builds the observation matrix

            O_t = P(e_t | X_t)

        given a noisy ghost distance evidence e_t and the current Pacman
        position.

        Arguments:
            walls: The W x H grid of walls.
            evidence: A noisy ghost distance evidence e_t.
            position: The current position of Pacman.

        Returns:
            The W x H observation matrix O_t.
        """
        
        n = 4
        p = 0.5

        W,H = gridSize(walls)
        
        Observ = np.ndarray((W,H))
        
        for i in range(W):
            for j in range(H):
                trueDist = manhattanDistance(position,(i,j))
                z = trueDist + n*p
                Observ[i][j] = binom.pmf(n,p,z)
                
        return Observ

    def update(self, walls, belief, evidence, position):
        """Updates the previous ghost belief state

            b_{t-1} = P(X_{t-1} | e_{1:t-1})

        given a noisy ghost distance evidence e_t and the current Pacman
        position.

        Arguments:
            walls: The W x H grid of walls.
            belief: The belief state for the previous ghost position b_{t-1}.
            evidence: A noisy ghost distance evidence e_t.
            position: The current position of Pacman.

        Returns:
            The updated ghost belief state b_t as a W x H matrix.
        """

        T = self.transition_matrix(walls, position)
        O = self.observation_matrix(walls, evidence, position)

        return 0

    def get_action(self, state):
        """Updates the previous belief states given the current state.

        ! DO NOT MODIFY !

        Arguments:
            state: a game state. See API or class `pacman.GameState`.

        Returns:
            The list of updated belief states.
        """

        walls = state.getWalls()
        beliefs = state.getGhostBeliefStates()
        eaten = state.getGhostEaten()
        evidences = state.getGhostNoisyDistances()
        position = state.getPacmanPosition()

        new_beliefs = [None] * len(beliefs)

        for i in range(len(beliefs)):
            if eaten[i]:
                new_beliefs[i] = np.zeros_like(beliefs[i])
            else:
                new_beliefs[i] = self.update(
                    walls,
                    beliefs[i],
                    evidences[i],
                    position,
                )

        return new_beliefs


class PacmanAgent(Agent):
    """Pacman agent that tries to eat ghosts given belief states."""

    def __init__(self):
        super().__init__()

    def _get_action(self, walls, beliefs, eaten, position):
        """
        Arguments:
            walls: The W x H grid of walls.
            beliefs: The list of current ghost belief states.
            eaten: A list of booleans indicating which ghosts have been eaten.
            position: The current position of Pacman.

        Returns:
            A legal move as defined in `game.Directions`.
        """

        return Directions.STOP

    def get_action(self, state):
        """Given a Pacman game state, returns a legal move.

        ! DO NOT MODIFY !

        Arguments:
            state: a game state. See API or class `pacman.GameState`.

        Returns:
            A legal move as defined in `game.Directions`.
        """

        return self._get_action(
            state.getWalls(),
            state.getGhostBeliefStates(),
            state.getGhostEaten(),
            state.getPacmanPosition(),
        )